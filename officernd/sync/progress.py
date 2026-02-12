"""Progress tracking for sync operations via shared JSON file."""

import json
import logging
import os
import time
from typing import Optional

logger = logging.getLogger(__name__)

PROGRESS_FILE = "/tmp/officernd_sync_progress.json"


def reset_stale_progress():
    """Reset progress file if it says 'running' on startup (no sync thread exists yet).

    Called once at API startup. If the progress file says 'running', the previous
    process was killed and the sync thread is dead. Reset to idle so the UI
    does a smart check instead of auto-resuming a full sync.
    """
    try:
        if os.path.exists(PROGRESS_FILE):
            with open(PROGRESS_FILE, "r") as f:
                data = json.load(f)
            if data.get("status") == "running":
                logger.info("Resetting stale 'running' progress to 'idle' on startup")
                data["status"] = "idle"
                data["message"] = "Reset on startup"
                data["error"] = None
                with open(PROGRESS_FILE, "w") as f:
                    json.dump(data, f)
    except Exception as e:
        logger.warning(f"Failed to reset progress: {e}")


def update_progress(
    phase: str,
    status: str,
    current: int = 0,
    total: int = 0,
    endpoint: str = "",
    company: str = "",
    message: str = "",
    error: Optional[str] = None,
):
    """Write sync progress to shared JSON file for web UI polling."""
    data = {
        "phase": phase,
        "status": status,
        "current": current,
        "total": total,
        "endpoint": endpoint,
        "company": company,
        "message": message,
        "error": error,
        "timestamp": time.time(),
    }
    try:
        with open(PROGRESS_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        logger.warning(f"Failed to write progress file: {e}")


STALE_THRESHOLD = 900  # seconds - large endpoints can take long with rate limiting (429 backoff)


def read_progress() -> dict:
    """Read current sync progress from shared JSON file.

    If progress says 'running' but timestamp is stale (>120s old),
    the sync thread was likely killed (e.g. by deployment). Reset to idle.
    """
    try:
        if os.path.exists(PROGRESS_FILE):
            with open(PROGRESS_FILE, "r") as f:
                data = json.load(f)
            # Detect stale running state (sync thread killed by deployment)
            if data.get("status") == "running" and data.get("timestamp"):
                age = time.time() - data["timestamp"]
                if age > STALE_THRESHOLD:
                    logger.warning(f"Stale sync progress detected ({int(age)}s old). Resetting to idle.")
                    data["status"] = "error"
                    data["error"] = f"Sync interrupted (no update for {int(age)}s)"
                    data["message"] = "Sync was interrupted - please restart"
            return data
    except Exception as e:
        logger.warning(f"Failed to read progress file: {e}")
    return {"status": "idle", "phase": "", "current": 0, "total": 0, "message": "No sync running"}
