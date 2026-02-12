"""
Sync entry points required by api/sync_routes.py.

Exports:
    sync_endpoint(client, endpoint, resume) -> dict
    sync_all_endpoints(client, endpoints, resume, max_workers) -> list[dict]
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from db.engine import session_context
from db.models import SyncJob
from sync.pipeline import sync_endpoint_pipeline

logger = logging.getLogger(__name__)

# All global endpoints that can be synced individually
GLOBAL_ENDPOINTS = [
    "companies", "visitors", "resources", "resource-types", "locations",
    "floors", "posts", "events", "tickets", "ticket-options", "charges",
    "tax-rates", "revenue-accounts", "plans", "resource-rates", "visits",
    "webhooks",
]


def _get_or_create_event_loop():
    """Get running event loop or create a new one."""
    try:
        loop = asyncio.get_running_loop()
        return loop
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


def sync_endpoint(client, endpoint: str, resume: bool = False) -> Dict[str, Any]:
    """
    Sync a single endpoint. Called from sync_routes.py background thread.

    Creates a SyncJob record to track progress, then runs the async pipeline.
    """
    # Create sync job record
    job_id = _create_sync_job(endpoint)

    try:
        # Get resume cursor if applicable
        resume_cursor = None
        if resume:
            resume_cursor = _get_last_cursor(endpoint)

        # Run the async pipeline
        loop = _get_or_create_event_loop()
        result = loop.run_until_complete(
            sync_endpoint_pipeline(client, endpoint, resume_cursor=resume_cursor)
        )

        # Update sync job with results
        _complete_sync_job(
            job_id,
            status=result["status"],
            records_fetched=result["records_fetched"],
            records_upserted=result["records_upserted"],
            error=result.get("error"),
        )

        return result

    except Exception as e:
        _complete_sync_job(job_id, status="failed", error=str(e))
        raise


def sync_all_endpoints(
    client,
    endpoints: Optional[List[str]] = None,
    resume: bool = False,
    max_workers: int = 4,
) -> List[Dict[str, Any]]:
    """
    Sync multiple endpoints. Called from sync_routes.py background thread.

    If endpoints is None, syncs all global endpoints.
    """
    target_endpoints = endpoints or GLOBAL_ENDPOINTS
    results = []

    for endpoint in target_endpoints:
        try:
            result = sync_endpoint(client, endpoint, resume=resume)
            results.append(result)
        except Exception as e:
            logger.error(f"Sync failed for {endpoint}: {e}")
            results.append({
                "endpoint": endpoint,
                "status": "failed",
                "records_fetched": 0,
                "records_upserted": 0,
                "error": str(e),
            })

    return results


def _create_sync_job(endpoint: str) -> int:
    """Create a new SyncJob record and return its ID."""
    with session_context() as session:
        job = SyncJob(
            endpoint=endpoint,
            status="in_progress",
            started_at=datetime.now(timezone.utc),
            records_fetched=0,
            records_upserted=0,
        )
        session.add(job)
        session.flush()
        return job.id


def _complete_sync_job(
    job_id: int,
    status: str = "completed",
    records_fetched: int = 0,
    records_upserted: int = 0,
    error: Optional[str] = None,
):
    """Update a SyncJob record with completion status."""
    with session_context() as session:
        job = session.query(SyncJob).filter(SyncJob.id == job_id).first()
        if job:
            job.status = status
            job.records_fetched = records_fetched
            job.records_upserted = records_upserted
            job.error_message = error
            job.completed_at = datetime.now(timezone.utc)


def _get_last_cursor(endpoint: str) -> Optional[str]:
    """Get the last cursor from the most recent completed sync job."""
    with session_context() as session:
        job = (
            session.query(SyncJob)
            .filter(SyncJob.endpoint == endpoint, SyncJob.status == "completed")
            .order_by(SyncJob.completed_at.desc())
            .first()
        )
        return job.last_cursor if job else None
