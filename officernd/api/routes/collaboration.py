"""
Collaboration API routes for OfficeRnD API Offline Clone.

This module provides FastAPI routes for Collaboration API endpoints:
- GET /posts + GET /posts/{id}
- GET /events + GET /events/{id}
- GET /tickets (filter: status, company, member, location, assignedTo)
- GET /tickets/{id}
- GET /ticket-options
"""

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Query

from db.engine import session_context
from db.models import Post, Event, Ticket, TicketOption
from api.routes import paginated_query, apply_filters, get_single, count_query

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/collaboration", tags=["Collaboration"])


@router.get("/posts")
async def get_posts(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
) -> Dict[str, Any]:
    """Get all posts with pagination."""
    with session_context() as session:
        return paginated_query(
            session, Post,
            limit=limit or 100, offset=offset or 0,
            filters={},
        )


@router.get("/events")
async def get_events(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
) -> Dict[str, Any]:
    """Get all events with pagination."""
    with session_context() as session:
        return paginated_query(
            session, Event,
            limit=limit or 100, offset=offset or 0,
            filters={},
        )


@router.get("/events/count")
async def get_events_count() -> Dict[str, Any]:
    """Get total count of events."""
    with session_context() as session:
        return count_query(session, Event)


@router.get("/events/{event_id}")
async def get_event(event_id: str) -> Dict[str, Any]:
    """Get a single event by ID."""
    with session_context() as session:
        return get_single(session, Event, event_id)


@router.get("/posts/{post_id}")
async def get_post(post_id: str) -> Dict[str, Any]:
    """Get a single post by ID."""
    with session_context() as session:
        return get_single(session, Post, post_id)


@router.get("/tickets")
async def get_tickets(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    status: Optional[str] = Query(None),
    company: Optional[str] = Query(None),
    member: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    assignedTo: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Get all tickets with optional filtering and pagination."""
    filters = {}
    if status:
        filters["status"] = status
    if company:
        filters["company_id"] = company
    if member:
        filters["member_id"] = member
    if location:
        filters["location_id"] = location
    if assignedTo:
        filters["assigned_to"] = assignedTo

    with session_context() as session:
        return paginated_query(
            session, Ticket,
            limit=limit or 100, offset=offset or 0,
            filters=apply_filters(Ticket, filters),
        )


@router.get("/tickets/count")
async def get_tickets_count(
    countBy: Optional[str] = Query(None, alias="$countBy"),
) -> Dict[str, Any]:
    """Get total count of tickets, optionally grouped by a field."""
    with session_context() as session:
        return count_query(session, Ticket, count_by=countBy)


@router.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: str) -> Dict[str, Any]:
    """Get a single ticket by ID."""
    with session_context() as session:
        return get_single(session, Ticket, ticket_id)


@router.get("/ticket-options")
async def get_ticket_options(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
) -> Dict[str, Any]:
    """Get all ticket options with pagination."""
    with session_context() as session:
        return paginated_query(
            session, TicketOption,
            limit=limit or 100, offset=offset or 0,
            filters={},
        )
