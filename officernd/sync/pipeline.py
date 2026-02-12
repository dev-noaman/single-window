"""ETL pipeline: fetch all pages -> parallel save (JSON + DB) via asyncio.gather."""

import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional

from sync.fetcher import fetch_all_pages
from sync.json_writer import save_json
from sync.writer import upsert_records

logger = logging.getLogger(__name__)


async def sync_endpoint_pipeline(
    client,
    endpoint: str,
    query_params: Optional[Dict[str, Any]] = None,
    company_id: Optional[str] = None,
    resume_cursor: Optional[str] = None,
    parent_id_field: Optional[str] = None,
    parent_id_value: Optional[str] = None,
    heartbeat_fn: Optional[Callable] = None,
    max_pages: int = 0,
) -> Dict[str, Any]:
    """
    Full ETL pipeline for one endpoint:
    1. Fetch all pages (cursor-based pagination)
    2. Save to JSON + DB in parallel

    Returns result dict with records_fetched and records_upserted.
    """
    result = {
        "endpoint": endpoint,
        "records_fetched": 0,
        "records_upserted": 0,
        "status": "completed",
        "error": None,
    }

    try:
        # Fetch all pages
        records = await fetch_all_pages(
            client, endpoint, query_params=query_params, resume_cursor=resume_cursor,
            heartbeat_fn=heartbeat_fn, max_pages=max_pages,
        )
        result["records_fetched"] = len(records)

        if not records:
            return result

        # Save JSON + DB in parallel
        json_task = asyncio.to_thread(save_json, endpoint, records, company_id)
        db_task = asyncio.to_thread(
            upsert_records, endpoint, records,
            parent_id_field=parent_id_field,
            parent_id_value=parent_id_value,
        )

        _, upserted = await asyncio.gather(json_task, db_task)
        result["records_upserted"] = upserted

    except Exception as e:
        logger.error(f"Pipeline failed for {endpoint}: {e}")
        result["status"] = "failed"
        result["error"] = str(e)

    return result
