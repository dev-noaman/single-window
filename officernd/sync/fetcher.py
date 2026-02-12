"""Paginated API fetcher with cursor-based pagination and deduplication."""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

MAX_RETRIES = 5
BACKOFF_BASE = 2  # seconds
DEFAULT_MAX_PAGES = 500  # Safety cap for per-company: 500 pages x 50 = 25,000 records


async def fetch_all_pages(
    client,
    resource: str,
    query_params: Optional[Dict[str, Any]] = None,
    resume_cursor: Optional[str] = None,
    heartbeat_fn=None,
    max_pages: int = 0,
) -> List[Dict[str, Any]]:
    """
    Fetch all pages of an endpoint using cursor-based pagination.

    Uses $cursorNext query param (with $ prefix) for pagination.
    Response body returns cursorNext (no $).
    Deduplicates by _id to handle overlapping pages.
    Retries up to 5 times with exponential backoff.
    """
    all_records: List[Dict[str, Any]] = []
    seen_ids: set = set()
    cursor = resume_cursor
    page = 0

    while True:
        page += 1
        params = dict(query_params or {})
        if cursor:
            params["$cursorNext"] = cursor

        records, next_cursor = await _fetch_page_with_retry(client, resource, params, page)

        # Deduplicate by _id
        for record in records:
            record_id = record.get("_id")
            if record_id and record_id not in seen_ids:
                seen_ids.add(record_id)
                all_records.append(record)

        # Send heartbeat so stale detector doesn't kill us during long fetches
        if heartbeat_fn and page % 10 == 0:
            try:
                heartbeat_fn(resource, page, len(all_records))
            except Exception:
                pass

        if not next_cursor or not records:
            break

        # Safety cap to prevent infinite pagination on huge endpoints
        if max_pages > 0 and page >= max_pages:
            logger.warning(f"Hit max_pages ({max_pages}) for {resource}, stopping. Got {len(all_records)} records.")
            break

        cursor = next_cursor

    logger.info(f"Fetched {len(all_records)} records from {resource} ({page} pages)")
    return all_records


async def _fetch_page_with_retry(
    client,
    resource: str,
    params: Dict[str, Any],
    page: int,
) -> tuple:
    """Fetch a single page with exponential backoff retry."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = await asyncio.to_thread(
                client.get, resource, query_params=params
            )

            # Unwrap ApiResponse to get the raw payload
            if hasattr(response, 'payload'):
                if response.error:
                    raise Exception(f"API error {response.status_code}: {response.error}")
                data = response.payload
            else:
                data = response

            # Handle different response formats
            if isinstance(data, dict):
                records = data.get("results", [])
                if not records and isinstance(data.get("results"), type(None)):
                    # No "results" key — treat entire dict as unexpected format
                    records = []
                next_cursor = data.get("cursorNext")
            elif isinstance(data, list):
                records = data
                next_cursor = None
            else:
                records = []
                next_cursor = None

            return records, next_cursor

        except Exception as e:
            error_str = str(e)

            # Don't retry client errors (HTTP 400) - they will never succeed
            if "API error 400" in error_str:
                logger.warning(f"Skipping {resource} page {page}: client error (400) - {e}")
                raise

            if attempt == MAX_RETRIES:
                logger.error(f"Failed to fetch {resource} page {page} after {MAX_RETRIES} attempts: {e}")
                raise

            # Use longer backoff for rate limiting (429)
            if "429" in error_str or "too many" in error_str.lower():
                wait = 30 * attempt  # 30s, 60s, 90s, 120s for rate limits
            else:
                wait = BACKOFF_BASE ** attempt

            logger.warning(f"Fetch {resource} page {page} attempt {attempt} failed: {e}. Retrying in {wait}s...")
            await asyncio.sleep(wait)

    return [], None
