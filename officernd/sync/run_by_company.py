"""
3-phase sync orchestrator for OfficeRnD data.

Phase 1: Global endpoints (22) - fetched once, all pages
Phase 2: Per-company endpoints (579 active companies x 13 endpoints)
Phase 3: Dependent endpoints (payment documents, membership assignments)

Supports --incremental mode: only sync NEW companies added since last run.
"""

import argparse
import asyncio
import logging
import os
import sys
import time
from datetime import datetime, timezone, timedelta
from typing import List, Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from api.client import OfficeRnDClient
from api.config import AppConfig
from db.engine import session_context
from db.models import Company, Membership, Payment, SyncJob, SyncJobCompany
from sync.pipeline import sync_endpoint_pipeline
from sync.progress import update_progress

logger = logging.getLogger(__name__)

# Phase 1 - Global endpoints (synced once, all pages)
GLOBAL_ENDPOINTS = [
    "companies", "visitors", "resources", "resource-types", "locations",
    "floors", "posts", "events", "tickets", "ticket-options", "charges",
    "tax-rates", "revenue-accounts", "plans", "resource-rates", "visits",
    "webhooks",
    # Settings/config endpoints
    "amenities", "benefits", "custom-properties", "opportunity-statuses",
    "secondary-currencies",
]

# Phase 2 - Per-company endpoints
COMPANY_ENDPOINTS = [
    "members", "bookings", "bookings/occurrences", "memberships", "fees",
    "credits", "payments", "contracts", "checkins", "opportunities",
    "coins/stats",
    # New per-company endpoints
    "passes", "payment-details",
]


async def run_phase1(client, resume: bool = False) -> List[dict]:
    """Phase 1: Sync all global endpoints sequentially."""
    results = []
    total = len(GLOBAL_ENDPOINTS)

    for i, endpoint in enumerate(GLOBAL_ENDPOINTS, 1):
        update_progress(
            phase="Phase 1: Global",
            status="running",
            current=i,
            total=total,
            endpoint=endpoint,
            message=f"Syncing {endpoint}...",
        )

        # Create SyncJob record so StatusBar can query sync status
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
            job_id = job.id

        result = await sync_endpoint_pipeline(client, endpoint)
        results.append(result)

        # Update SyncJob with results
        with session_context() as session:
            job = session.query(SyncJob).filter(SyncJob.id == job_id).first()
            if job:
                job.status = result["status"]
                job.records_fetched = result["records_fetched"]
                job.records_upserted = result["records_upserted"]
                job.error_message = result.get("error")
                job.completed_at = datetime.now(timezone.utc)

        logger.info(
            f"Phase 1 [{i}/{total}] {endpoint}: "
            f"{result['records_fetched']} fetched, {result['records_upserted']} upserted"
        )

    return results


async def run_phase2(
    client,
    concurrency: int = 5,
    company_id: Optional[str] = None,
    status_filter: str = "active",
    incremental: bool = False,
    resume: bool = False,
) -> List[dict]:
    """Phase 2: Sync per-company endpoints for all active companies."""
    # Load company IDs from database
    companies = _get_companies(status_filter, company_id, incremental, resume)

    if not companies:
        logger.info("No companies to sync in Phase 2")
        update_progress(phase="Phase 2", status="running", message="No companies to sync")
        return []

    total_companies = len(companies)
    results = []
    semaphore = asyncio.Semaphore(concurrency)

    for idx, (cid, cname) in enumerate(companies, 1):
        update_progress(
            phase="Phase 2: Companies",
            status="running",
            current=idx,
            total=total_companies,
            company=f"{cname or cid}",
            message=f"Syncing company {idx}/{total_companies}...",
        )

        # Create company sync job
        job_id = _create_company_job(cid, cname)
        company_results = []

        for endpoint in COMPANY_ENDPOINTS:
            async with semaphore:
                try:
                    # Build resource path with company filter
                    query_params = {"company": cid}

                    # Add required params for specific endpoints
                    if endpoint == "bookings/occurrences":
                        now = datetime.now(timezone.utc)
                        query_params["seriesStart"] = (now - timedelta(days=365)).strftime("%Y-%m-%dT00:00:00Z")
                        query_params["seriesEnd"] = (now + timedelta(days=90)).strftime("%Y-%m-%dT00:00:00Z")
                    elif endpoint == "coins/stats":
                        query_params["month"] = datetime.now(timezone.utc).strftime("%Y-%m")

                    # Heartbeat callback to keep progress file fresh during long fetches
                    def _heartbeat(resource, page, records_so_far, _ep=endpoint):
                        update_progress(
                            phase="Phase 2: Companies",
                            status="running",
                            current=idx,
                            total=total_companies,
                            company=f"{cname or cid}",
                            endpoint=_ep,
                            message=f"Company {idx}/{total_companies} - {_ep} page {page} ({records_so_far} records)...",
                        )

                    result = await sync_endpoint_pipeline(
                        client, endpoint, query_params=query_params, company_id=cid,
                        heartbeat_fn=_heartbeat, max_pages=500,
                    )
                    company_results.append(result)
                except Exception as e:
                    logger.error(f"Company {cid} endpoint {endpoint} failed: {e}")
                    company_results.append({
                        "endpoint": endpoint,
                        "status": "failed",
                        "records_fetched": 0,
                        "records_upserted": 0,
                        "error": str(e),
                    })

        # Update company job
        completed = sum(1 for r in company_results if r["status"] == "completed")
        failed = sum(1 for r in company_results if r["status"] == "failed")
        total_fetched = sum(r["records_fetched"] for r in company_results)
        total_upserted = sum(r["records_upserted"] for r in company_results)

        _complete_company_job(
            job_id,
            status="completed" if failed == 0 else "partial",
            endpoints_completed=completed,
            endpoints_failed=failed,
            total_fetched=total_fetched,
            total_upserted=total_upserted,
        )

        results.extend(company_results)
        logger.info(
            f"Phase 2 [{idx}/{total_companies}] {cname or cid}: "
            f"{completed}/{len(COMPANY_ENDPOINTS)} endpoints, {total_fetched} records"
        )

    return results


async def run_backfill(client, concurrency: int = 5) -> List[dict]:
    """Backfill new endpoints (passes, payment-details) for companies synced with older code."""
    NEW_ENDPOINTS = ["passes", "payment-details"]

    with session_context() as session:
        # Find companies with fewer endpoints than current expected count
        from sqlalchemy import func as sqlfunc
        subq = (
            session.query(
                SyncJobCompany.company_id,
                sqlfunc.max(SyncJobCompany.id).label("max_id"),
            )
            .group_by(SyncJobCompany.company_id)
            .subquery()
        )
        stale_jobs = (
            session.query(SyncJobCompany)
            .join(subq, SyncJobCompany.id == subq.c.max_id)
            .filter(SyncJobCompany.endpoints_completed < len(COMPANY_ENDPOINTS))
            .filter(SyncJobCompany.status.in_(["completed", "partial"]))
            .all()
        )
        companies = [(j.company_id, j.company_name, j.id) for j in stale_jobs]

    if not companies:
        logger.info("No companies need backfill")
        return []

    total = len(companies)
    logger.info(f"Backfilling {len(NEW_ENDPOINTS)} endpoints for {total} companies")
    results = []
    semaphore = asyncio.Semaphore(concurrency)

    for idx, (cid, cname, job_id) in enumerate(companies, 1):
        update_progress(
            phase="Phase 2: Backfill",
            status="running",
            current=idx,
            total=total,
            company=f"{cname or cid}",
            message=f"Backfilling {idx}/{total}...",
        )

        company_results = []
        for endpoint in NEW_ENDPOINTS:
            async with semaphore:
                query_params = {"company": cid}
                result = await sync_endpoint_pipeline(
                    client, endpoint, query_params=query_params, company_id=cid,
                    max_pages=500,
                )
                company_results.append(result)

        completed = sum(1 for r in company_results if r["status"] == "completed")
        fetched = sum(r["records_fetched"] for r in company_results)
        upserted = sum(r["records_upserted"] for r in company_results)

        # Update existing company job record
        with session_context() as session:
            job = session.query(SyncJobCompany).filter(SyncJobCompany.id == job_id).first()
            if job:
                job.endpoints_completed = (job.endpoints_completed or 0) + completed
                job.total_records_fetched = (job.total_records_fetched or 0) + fetched
                job.total_records_upserted = (job.total_records_upserted or 0) + upserted

        results.extend(company_results)
        logger.info(f"Backfill [{idx}/{total}] {cname or cid}: +{completed} endpoints, +{fetched} records")

    return results


async def run_phase3(client) -> List[dict]:
    """Phase 3: Sync dependent endpoints (payment documents, assignments) with SyncJob tracking."""
    results = []

    # Skip Phase 3 if already completed (avoid re-running on resume)
    with session_context() as session:
        pd_done = session.query(SyncJob).filter(
            SyncJob.endpoint == "payment-documents", SyncJob.status == "completed"
        ).first()
        as_done = session.query(SyncJob).filter(
            SyncJob.endpoint == "assignments", SyncJob.status == "completed"
        ).first()
        if pd_done and as_done:
            logger.info("Phase 3 already completed (payment-documents + assignments). Skipping.")
            update_progress(
                phase="Phase 3: Dependent",
                status="running",
                message="Phase 3 already completed, skipping...",
            )
            return results

    # === Payment documents ===
    update_progress(
        phase="Phase 3: Dependent",
        status="running",
        message="Fetching payment documents...",
    )

    payment_ids = _get_all_payment_ids()
    total_payments = len(payment_ids)

    # Create SyncJob for payment-documents tracking
    with session_context() as session:
        pd_job = SyncJob(
            endpoint="payment-documents",
            status="in_progress",
            started_at=datetime.now(timezone.utc),
            records_fetched=0,
            records_upserted=0,
        )
        session.add(pd_job)
        session.flush()
        pd_job_id = pd_job.id

    pd_fetched = 0
    pd_upserted = 0

    for i, pid in enumerate(payment_ids, 1):
        if i % 10 == 0:
            update_progress(
                phase="Phase 3: Dependent",
                status="running",
                current=i,
                total=total_payments,
                endpoint="payment-documents",
                message=f"Payment docs {i}/{total_payments}...",
            )
            # Update SyncJob periodically (same frequency as progress)
            with session_context() as session:
                job = session.query(SyncJob).filter(SyncJob.id == pd_job_id).first()
                if job:
                    job.records_fetched = pd_fetched
                    job.records_upserted = pd_upserted

        result = await sync_endpoint_pipeline(
            client,
            f"payments/{pid}/documents",
            parent_id_field="payment_id",
            parent_id_value=pid,
        )
        pd_fetched += result["records_fetched"]
        pd_upserted += result["records_upserted"]
        results.append(result)

        # Small delay to avoid 429 rate limits
        await asyncio.sleep(0.1)

    # Complete payment-documents SyncJob
    with session_context() as session:
        job = session.query(SyncJob).filter(SyncJob.id == pd_job_id).first()
        if job:
            job.status = "completed"
            job.records_fetched = pd_fetched
            job.records_upserted = pd_upserted
            job.completed_at = datetime.now(timezone.utc)

    # === Membership assignments ===
    update_progress(
        phase="Phase 3: Dependent",
        status="running",
        message="Fetching membership assignments...",
    )

    membership_ids = _get_all_membership_ids()
    total_memberships = len(membership_ids)

    # Create SyncJob for assignments tracking
    with session_context() as session:
        as_job = SyncJob(
            endpoint="assignments",
            status="in_progress",
            started_at=datetime.now(timezone.utc),
            records_fetched=0,
            records_upserted=0,
        )
        session.add(as_job)
        session.flush()
        as_job_id = as_job.id

    as_fetched = 0
    as_upserted = 0

    for i, mid in enumerate(membership_ids, 1):
        if i % 10 == 0:
            update_progress(
                phase="Phase 3: Dependent",
                status="running",
                current=i,
                total=total_memberships,
                endpoint="assignments",
                message=f"Assignments {i}/{total_memberships}...",
            )
            # Update SyncJob periodically (same frequency as progress)
            with session_context() as session:
                job = session.query(SyncJob).filter(SyncJob.id == as_job_id).first()
                if job:
                    job.records_fetched = as_fetched
                    job.records_upserted = as_upserted

        result = await sync_endpoint_pipeline(
            client,
            "assignments",
            query_params={"membership": mid},
        )
        as_fetched += result["records_fetched"]
        as_upserted += result["records_upserted"]
        results.append(result)

        # Small delay to avoid 429 rate limits
        await asyncio.sleep(0.1)

    # Complete assignments SyncJob
    with session_context() as session:
        job = session.query(SyncJob).filter(SyncJob.id == as_job_id).first()
        if job:
            job.status = "completed"
            job.records_fetched = as_fetched
            job.records_upserted = as_upserted
            job.completed_at = datetime.now(timezone.utc)

    return results


async def run_full_sync(
    client,
    concurrency: int = 5,
    company_id: Optional[str] = None,
    status_filter: str = "active",
    incremental: bool = False,
    resume: bool = False,
):
    """Run all 3 phases of the sync + backfill."""
    start_time = time.time()

    update_progress(phase="Starting", status="running", message="Initializing sync...")

    # Phase 1 - Global (skip if single company or incremental that already has data)
    if not company_id:
        logger.info("=== Phase 1: Global Endpoints ===")
        await run_phase1(client, resume=resume)

    # Phase 2 - Per-company
    logger.info("=== Phase 2: Per-Company Endpoints ===")
    await run_phase2(
        client,
        concurrency=concurrency,
        company_id=company_id,
        status_filter=status_filter,
        incremental=incremental,
        resume=resume,
    )

    # Backfill: sync new endpoints for companies synced with older code
    if not company_id:
        logger.info("=== Backfill: New Endpoints ===")
        await run_backfill(client, concurrency=concurrency)

    # Phase 3 - Dependent
    if not company_id:
        logger.info("=== Phase 3: Dependent Endpoints ===")
        await run_phase3(client)

    elapsed = time.time() - start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)

    update_progress(
        phase="Complete",
        status="completed",
        message=f"Sync completed in {minutes}m {seconds}s",
    )

    logger.info(f"Full sync completed in {minutes}m {seconds}s")


# ============================================================================
# Database helpers
# ============================================================================

def _get_companies(
    status_filter: str,
    company_id: Optional[str],
    incremental: bool,
    resume: bool,
) -> List[tuple]:
    """Get list of (company_id, company_name) to sync."""
    with session_context() as session:
        if company_id:
            company = session.query(Company).filter(Company._id == company_id).first()
            return [(company_id, company.name if company else None)]

        query = session.query(Company._id, Company.name)

        if status_filter != "all":
            query = query.filter(Company.status == status_filter)

        companies = query.all()

        if incremental:
            # Only sync companies not yet in sync_jobs_company
            synced_ids = {
                row[0] for row in
                session.query(SyncJobCompany.company_id)
                .filter(SyncJobCompany.status.in_(["completed", "partial"]))
                .all()
            }
            companies = [(cid, cname) for cid, cname in companies if cid not in synced_ids]

        if resume:
            # Skip completed companies
            completed_ids = {
                row[0] for row in
                session.query(SyncJobCompany.company_id)
                .filter(SyncJobCompany.status == "completed")
                .all()
            }
            companies = [(cid, cname) for cid, cname in companies if cid not in completed_ids]

        return companies


def _get_all_payment_ids() -> List[str]:
    """Get all payment IDs from the database."""
    with session_context() as session:
        return [row[0] for row in session.query(Payment._id).all()]


def _get_all_membership_ids() -> List[str]:
    """Get all membership IDs from the database."""
    with session_context() as session:
        return [row[0] for row in session.query(Membership._id).all()]


def _create_company_job(company_id: str, company_name: Optional[str]) -> int:
    """Create a SyncJobCompany record."""
    with session_context() as session:
        job = SyncJobCompany(
            company_id=company_id,
            company_name=company_name,
            status="in_progress",
            started_at=datetime.now(timezone.utc),
        )
        session.add(job)
        session.flush()
        return job.id


def _complete_company_job(
    job_id: int,
    status: str,
    endpoints_completed: int = 0,
    endpoints_failed: int = 0,
    total_fetched: int = 0,
    total_upserted: int = 0,
):
    """Update a SyncJobCompany record with results."""
    with session_context() as session:
        job = session.query(SyncJobCompany).filter(SyncJobCompany.id == job_id).first()
        if job:
            job.status = status
            job.endpoints_completed = endpoints_completed
            job.endpoints_failed = endpoints_failed
            job.total_records_fetched = total_fetched
            job.total_records_upserted = total_upserted
            job.completed_at = datetime.now(timezone.utc)


# ============================================================================
# CLI entry point
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="OfficeRnD 3-phase sync orchestrator")
    parser.add_argument("--incremental", action="store_true", help="Only sync NEW companies")
    parser.add_argument("--resume", action="store_true", help="Resume interrupted sync")
    parser.add_argument("--company", type=str, help="Sync a single company by ID")
    parser.add_argument("--status", type=str, default="active", help="Company status filter (default: active)")
    parser.add_argument("--concurrency", type=int, default=5, help="Max concurrent requests")

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "sync.log"),
                encoding="utf-8",
            ),
        ],
    )

    # Load config and create client
    config = AppConfig.from_env()

    # Ensure DB schema is up to date (new tables + missing columns)
    from db.engine import ensure_schema
    ensure_schema()

    with OfficeRnDClient(config) as client:
        asyncio.run(
            run_full_sync(
                client,
                concurrency=args.concurrency,
                company_id=args.company,
                status_filter=args.status,
                incremental=args.incremental,
                resume=args.resume,
            )
        )


if __name__ == "__main__":
    main()
