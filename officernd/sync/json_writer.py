"""JSON file writer for sync data - organized by global and per-company folders."""

import json
import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def save_json(
    endpoint: str,
    records: List[Dict[str, Any]],
    company_id: Optional[str] = None,
) -> str:
    """
    Save records to organized JSON files.

    Global endpoints -> data/global/{endpoint}.json
    Per-company endpoints -> data/company_{id}/{endpoint}.json
    Dependent endpoints -> data/{type}/{parent_id}/{endpoint}.json
    """
    # Determine output directory
    if company_id:
        out_dir = os.path.join(DATA_DIR, f"company_{company_id}")
    else:
        out_dir = os.path.join(DATA_DIR, "global")

    os.makedirs(out_dir, exist_ok=True)

    # Sanitize endpoint name for filename
    filename = endpoint.replace("/", "_").replace("?", "_") + ".json"
    filepath = os.path.join(out_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2, default=str)

    logger.debug(f"Saved {len(records)} records to {filepath}")
    return filepath
