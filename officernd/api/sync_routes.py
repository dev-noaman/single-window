"""
Sync management endpoints for OfficeRnD API Offline Clone.

This module provides FastAPI routes for sync management:
- GET /sync/status (returns sync_jobs summary)
- GET /sync/progress (returns real-time progress from shared file)
- POST /sync/run (triggers sync in background thread - full, incremental, or smart)
- GET /sync/export (export all DB tables as ZIP of CSVs)
"""

import asyncio
import csv
import io
import json
import logging
import threading
import time
import zipfile
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, status
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from api.config import AppConfig
from sqlalchemy import func, inspect as sa_inspect, text
from db.engine import get_engine, session_context
from db.models import Company, SyncJob, SyncJobCompany
from sync.run import sync_endpoint, sync_all_endpoints
from sync.run_by_company import GLOBAL_ENDPOINTS, COMPANY_ENDPOINTS
from sync.progress import read_progress, update_progress

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/sync", tags=["Sync Management"])

AUTO_SYNC_INTERVAL = 3600  # seconds (1 hour)


class SyncRequest(BaseModel):
    """Request model for triggering sync."""
    endpoint: Optional[str] = None
    resume: bool = False
    mode: str = "full"  # "full" or "incremental"


class SyncStatusResponse(BaseModel):
    """Response model for sync status."""
    endpoint: str
    status: str  # pending, in_progress, completed, failed
    records_fetched: int
    records_upserted: int
    last_run: Optional[str] = None
    error: Optional[str] = None


@router.get("/status", response_model=List[SyncStatusResponse])
async def get_sync_status(
    endpoint: Optional[str] = Query(None),
) -> List[SyncStatusResponse]:
    """
    Get sync status for all endpoints.

    Query Parameters:
        endpoint: Optional filter by endpoint name

    Returns:
        List of sync status for each endpoint
    """
    with session_context() as session:
        query = session.query(SyncJob)

        if endpoint:
            query = query.filter(SyncJob.endpoint == endpoint)

        jobs = query.order_by(SyncJob.created_at.desc()).all()

        return [
            SyncStatusResponse(
                endpoint=job.endpoint,
                status=job.status,
                records_fetched=job.records_fetched,
                records_upserted=job.records_upserted,
                last_run=job.completed_at.isoformat() if job.completed_at else None,
                error=job.error_message,
            )
            for job in jobs
        ]


@router.get("/companies")
async def get_sync_companies() -> List[Dict[str, Any]]:
    """Get per-company sync results from sync_jobs_company table."""
    with session_context() as session:
        jobs = (
            session.query(SyncJobCompany)
            .order_by(SyncJobCompany.completed_at.desc().nullslast(), SyncJobCompany.id.desc())
            .all()
        )

        # Deduplicate: keep only the latest job per company_id
        seen = set()
        results = []
        for job in jobs:
            if job.company_id in seen:
                continue
            seen.add(job.company_id)
            results.append({
                "company_id": job.company_id,
                "company_name": job.company_name,
                "status": job.status,
                "endpoints_completed": job.endpoints_completed or 0,
                "endpoints_failed": job.endpoints_failed or 0,
                "records_fetched": job.total_records_fetched or 0,
                "records_upserted": job.total_records_upserted or 0,
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            })

        return results


@router.get("/stats")
async def get_sync_stats() -> Dict[str, Any]:
    """Get aggregate company counts by status and sync progress."""
    with session_context() as session:
        status_counts = (
            session.query(Company.status, func.count())
            .group_by(Company.status)
            .all()
        )
        counts = {s: c for s, c in status_counts}
        total = sum(counts.values())

        synced = (
            session.query(func.count(func.distinct(SyncJobCompany.company_id)))
            .filter(SyncJobCompany.status.in_(["completed", "partial"]))
            .scalar()
        ) or 0

        return {
            "companies_total": total,
            "companies_active": counts.get("active", 0),
            "companies_by_status": counts,
            "companies_synced": synced,
        }


@router.get("/phases")
async def get_sync_phases() -> Dict[str, Any]:
    """Get phase-level sync summary for the Phase Progress Tracker UI.

    Two phases:
      Phase 1 - Sync All Data: global endpoints (17) + per-company (579).
                Complete only when ALL active companies are synced.
      Phase 2 - Dependent: payment documents + membership assignments.
    """
    progress = read_progress()
    current_phase_name = progress.get("phase", "")

    with session_context() as session:
        # --- Global endpoints (sub-step of Phase 1) ---
        global_endpoints = []
        for ep in GLOBAL_ENDPOINTS:
            job = (
                session.query(SyncJob)
                .filter(SyncJob.endpoint == ep)
                .order_by(SyncJob.created_at.desc())
                .first()
            )
            if job:
                global_endpoints.append({
                    "endpoint": ep,
                    "status": job.status,
                    "records_fetched": job.records_fetched or 0,
                    "records_upserted": job.records_upserted or 0,
                    "last_run": job.completed_at.isoformat() if job.completed_at else None,
                    "error": job.error_message,
                })
            else:
                global_endpoints.append({
                    "endpoint": ep,
                    "status": "pending",
                    "records_fetched": 0,
                    "records_upserted": 0,
                    "last_run": None,
                    "error": None,
                })

        globals_completed = sum(1 for e in global_endpoints if e["status"] == "completed")
        globals_total = len(GLOBAL_ENDPOINTS)

        # --- Total active companies ---
        total_active = (
            session.query(func.count())
            .select_from(Company)
            .filter(Company.status == "active")
            .scalar()
        ) or 0

        # --- Company sync progress (part of Phase 1) ---
        # Always count distinct completed companies from DB as baseline
        db_completed = (
            session.query(func.count(func.distinct(SyncJobCompany.company_id)))
            .filter(SyncJobCompany.status.in_(["completed", "partial"]))
            .scalar()
        ) or 0

        if progress.get("status") == "running" and "Phase 2" in current_phase_name:
            # In resume mode, progress.total is only remaining companies (e.g. 388),
            # not all active (580). Calculate: already_done + current_progress
            progress_current = progress.get("current", 0)
            progress_total = progress.get("total", 0)
            already_done = max(0, total_active - progress_total) if progress_total < total_active else 0
            companies_completed = already_done + progress_current
        else:
            companies_completed = db_completed

        # --- Phase 2: dependent endpoints ---
        dep_endpoints = []
        for dep_ep in ["payment-documents", "assignments"]:
            job = (
                session.query(SyncJob)
                .filter(SyncJob.endpoint == dep_ep)
                .order_by(SyncJob.created_at.desc())
                .first()
            )
            if job:
                dep_endpoints.append({
                    "endpoint": dep_ep,
                    "status": job.status,
                    "records_fetched": job.records_fetched or 0,
                    "records_upserted": job.records_upserted or 0,
                })
            else:
                dep_endpoints.append({
                    "endpoint": dep_ep,
                    "status": "pending",
                    "records_fetched": 0,
                    "records_upserted": 0,
                })

        dep_completed = sum(1 for e in dep_endpoints if e["status"] == "completed")

    # Phase 1 is complete ONLY when all companies are synced
    all_companies_done = companies_completed >= total_active and total_active > 0

    # Determine statuses
    is_running = progress.get("status") == "running"

    if is_running:
        if "Phase 1" in current_phase_name or current_phase_name == "Starting" or "Phase 2" in current_phase_name:
            p1_status = "running"
            # Phase 2 may already be completed from a previous sync run
            p2_status = "completed" if dep_completed == 2 else "pending"
        elif "Phase 3" in current_phase_name:
            p1_status = "completed"
            p2_status = "running"
        else:
            p1_status = "completed" if all_companies_done else "running"
            p2_status = "completed" if dep_completed == 2 else "pending"
    else:
        p1_status = "completed" if all_companies_done else "pending"
        p2_status = "completed" if dep_completed == 2 else "pending"

    current_phase = ""
    if is_running:
        if p1_status == "running":
            current_phase = "Phase 1"
        elif p2_status == "running":
            current_phase = "Phase 2"

    # Sub-status for Phase 1: show whether syncing global endpoints or companies
    p1_sub = None
    if is_running and p1_status == "running":
        if "Phase 1" in current_phase_name or current_phase_name == "Starting":
            p1_sub = f"Global endpoints ({globals_completed}/{globals_total})"
        elif "Phase 2" in current_phase_name:
            p1_sub = f"Companies ({companies_completed}/{total_active})"

    return {
        "current_phase": current_phase,
        "phases": [
            {
                "phase": 1,
                "name": "Sync All Data",
                "status": p1_status,
                "completed": companies_completed,
                "total": total_active,
                "sub_status": p1_sub,
                "globals_completed": globals_completed,
                "globals_total": globals_total,
                "endpoints": global_endpoints,
            },
            {
                "phase": 2,
                "name": "Dependent",
                "status": p2_status,
                "completed": dep_completed,
                "total": 2,
                "endpoints": dep_endpoints,
            },
        ],
    }


@router.get("/progress")
async def get_sync_progress() -> Dict[str, Any]:
    """
    Get real-time sync progress from shared file.
    Used by web UI for progress polling.
    """
    return read_progress()


@router.get("/export")
async def export_database():
    """Export full PostgreSQL database backup using pg_dump."""
    import subprocess
    from urllib.parse import urlparse

    config = AppConfig.from_env()
    db_url = config.database.database_url
    parsed = urlparse(db_url)

    env = {
        "PGPASSWORD": parsed.password or "",
        "PATH": "/usr/bin:/usr/local/bin:/bin",
    }
    host = parsed.hostname or "localhost"
    port = str(parsed.port or 5432)
    dbname = parsed.path.lstrip("/")
    user = parsed.username or "officernd_user"

    try:
        result = subprocess.run(
            ["pg_dump", "-h", host, "-p", port, "-U", user, "-d", dbname,
             "--no-owner", "--no-acl", "--clean", "--if-exists"],
            capture_output=True,
            env=env,
            timeout=120,
        )
        if result.returncode != 0:
            raise Exception(result.stderr.decode().strip())
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="pg_dump not found on server")

    sql_bytes = result.stdout
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"officernd-backup-{timestamp}.sql"

    return StreamingResponse(
        io.BytesIO(sql_bytes),
        media_type="application/sql",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/run")
async def trigger_sync(
    request: SyncRequest,
    background_tasks: BackgroundTasks,
) -> Dict[str, Any]:
    """
    Trigger sync operation in background thread.

    Request Body:
        endpoint: Optional single endpoint to sync (None = all)
        resume: Whether to resume from last cursor
        mode: "full" or "incremental"

    Returns:
        Sync operation started response
    """
    # Load configuration
    try:
        config = AppConfig.from_env()
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Configuration error: {str(e)}",
        )

    # Guard: reject if a sync is already running
    current = read_progress()
    if current.get("status") == "running":
        return {
            "status": "already_running",
            "mode": request.mode,
            "message": "Sync already in progress",
        }

    # Create API client for sync
    from api.client import OfficeRnDClient

    # Define sync function for background thread
    def run_sync():
        with OfficeRnDClient(config) as client:
            try:
                if request.mode == "smart":
                    _run_smart_sync(client)
                elif request.mode == "incremental":
                    from sync.run_by_company import run_full_sync
                    _run_async(run_full_sync(client, incremental=True))
                elif request.endpoint:
                    sync_endpoint(client, request.endpoint, request.resume)
                else:
                    from sync.run_by_company import run_full_sync
                    _run_async(run_full_sync(client, resume=request.resume))
            except Exception as e:
                logger.error(f"Sync failed: {e}")
                update_progress(
                    phase="Error",
                    status="error",
                    error=str(e),
                    message=f"Sync failed: {e}",
                )

    # Run sync in background thread
    thread = threading.Thread(target=run_sync, daemon=True)
    thread.start()

    logger.info(f"Sync started: mode={request.mode}, endpoint={request.endpoint or 'all'}, resume={request.resume}")

    return {
        "status": "started",
        "mode": request.mode,
        "endpoint": request.endpoint or "all",
        "message": "Sync operation started in background thread",
    }


# ─── Module-level helpers (used by both trigger_sync and auto-scheduler) ───


def _run_async(coro):
    """Helper to run async coroutine in a new event loop."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(coro)
    finally:
        loop.close()


def _fetch_live_active(client, synced_ids: set):
    """Fetch active companies from live OfficeRnD API.

    Compares each company ID against synced_ids during pagination.
    Returns (total_count, list_of_new_company_objects).
    Only collects full objects for NEW companies (not yet synced).
    """
    total_count = 0
    new_companies = []
    cursor = None

    while True:
        params = {"status": "active", "$limit": "50"}
        if cursor:
            params["$cursorNext"] = cursor

        resp = client.get("companies", params)
        if resp.error:
            raise Exception(f"API error: {resp.error}")

        payload = resp.payload
        if not isinstance(payload, dict):
            break

        results = payload.get("results", [])
        total_count += len(results)

        for company in results:
            cid = company.get("_id")
            if cid and cid not in synced_ids:
                new_companies.append(company)

        cursor = payload.get("cursorNext")
        if not cursor or not results:
            break

    return total_count, new_companies


def _run_smart_sync(client):
    """Smart sync: fetch live active, compare IDs with synced, sync only new."""
    update_progress(
        phase="Checking",
        status="running",
        message="Checking OfficeRnD for new companies...",
    )

    # Step 1: Get synced company IDs from DB
    with session_context() as session:
        synced_ids = {
            row[0] for row in
            session.query(SyncJobCompany.company_id)
            .filter(SyncJobCompany.status.in_(["completed", "partial"]))
            .all()
        }

    # Step 2: Fetch active companies from live API, identify new ones
    t0 = time.time()
    try:
        live_count, new_companies = _fetch_live_active(client, synced_ids)
    except Exception as e:
        update_progress(
            phase="Error",
            status="error",
            error=str(e),
            message=f"API check failed: {e}",
        )
        return
    elapsed = time.time() - t0

    # Step 3: No new companies
    if not new_companies:
        update_progress(
            phase="Complete",
            status="completed",
            message=f"Already up to date ({len(synced_ids)}/{live_count} active companies synced) checked in {elapsed:.1f}s",
        )
        logger.info(f"Smart sync: up to date ({len(synced_ids)}/{live_count}) in {elapsed:.1f}s")
        return

    # Step 4: Show which companies are new
    new_names = ", ".join(
        (c.get("name") or c.get("_id", "?"))[:30] for c in new_companies[:3]
    )
    if len(new_companies) > 3:
        new_names += f" +{len(new_companies) - 3} more"

    logger.info(f"Smart sync: {len(new_companies)} new companies ({new_names}) checked in {elapsed:.1f}s")
    update_progress(
        phase="Starting",
        status="running",
        message=f"Found {len(new_companies)} new: {new_names}",
    )

    # Step 5: Save new companies to DB (so per-company sync can find them)
    from sync.writer import upsert_records
    upsert_records("companies", new_companies)
    logger.info(f"Saved {len(new_companies)} new companies to DB")

    # Step 6: Sync per-company endpoints for each new company only
    from sync.run_by_company import run_phase2

    async def _sync_new():
        total = len(new_companies)
        for idx, company in enumerate(new_companies, 1):
            cid = company["_id"]
            await run_phase2(client, company_id=cid)

        update_progress(
            phase="Complete",
            status="completed",
            message=f"Synced {total} new companies in {time.time() - t0:.1f}s",
        )

    _run_async(_sync_new())


# ─── Auto-sync scheduler (runs smart sync every hour in background) ───


def start_auto_sync_scheduler():
    """Start a daemon thread that runs smart sync every AUTO_SYNC_INTERVAL seconds."""

    def _scheduler_loop():
        logger.info(f"Auto-sync scheduler started (interval: {AUTO_SYNC_INTERVAL}s)")
        while True:
            time.sleep(AUTO_SYNC_INTERVAL)
            # Skip if a sync is already running
            current = read_progress()
            if current.get("status") == "running":
                logger.info("Auto-sync: skipped (sync already running)")
                continue
            logger.info("Auto-sync: starting scheduled smart sync...")
            try:
                config = AppConfig.from_env()
                from api.client import OfficeRnDClient
                with OfficeRnDClient(config) as client:
                    _run_smart_sync(client)
            except Exception as e:
                logger.error(f"Auto-sync failed: {e}")

    thread = threading.Thread(target=_scheduler_loop, daemon=True, name="auto-sync-scheduler")
    thread.start()
    return thread
