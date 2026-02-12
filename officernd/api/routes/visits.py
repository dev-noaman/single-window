"""
Visits API routes for OfficeRnD API Offline Clone.

This module provides FastAPI routes for Visits API endpoints:
- GET /visits (filter: member, visitor, location)
- GET /visits/{id}
- GET /checkins (filter: member, company, location)
- GET /checkins/{id}
"""

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Query

from db.engine import session_context
from db.models import Visit, Checkin
from api.routes import paginated_query, apply_filters, get_single

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/visits", tags=["Visits"])


@router.get("/visits")
async def get_visits(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    member: Optional[str] = Query(None),
    visitor: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Get all visits with optional filtering and pagination."""
    filters = {}
    if member:
        filters["member_id"] = member
    if visitor:
        filters["visitor_id"] = visitor
    if location:
        filters["location_id"] = location

    with session_context() as session:
        return paginated_query(
            session, Visit,
            limit=limit or 100, offset=offset or 0,
            filters=apply_filters(Visit, filters),
        )


@router.get("/visits/{visit_id}")
async def get_visit(visit_id: str) -> Dict[str, Any]:
    """Get a single visit by ID."""
    with session_context() as session:
        return get_single(session, Visit, visit_id)


@router.get("/checkins")
async def get_checkins(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    member: Optional[str] = Query(None),
    company: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Get all checkins with optional filtering and pagination."""
    filters = {}
    if member:
        filters["member_id"] = member
    if company:
        filters["company_id"] = company
    if location:
        filters["location_id"] = location

    with session_context() as session:
        return paginated_query(
            session, Checkin,
            limit=limit or 100, offset=offset or 0,
            filters=apply_filters(Checkin, filters),
        )


@router.get("/checkins/{checkin_id}")
async def get_checkin(checkin_id: str) -> Dict[str, Any]:
    """Get a single checkin by ID."""
    with session_context() as session:
        return get_single(session, Checkin, checkin_id)
