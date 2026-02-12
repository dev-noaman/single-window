"""
Space API routes for OfficeRnD API Offline Clone.

This module provides FastAPI routes for Space API endpoints:
- GET /resources (filter: type, location, floor, _id, name)
- GET /resources/{id}
- GET /resource-types
- GET /bookings (filter: resource, company, member, location)
- GET /bookings/{id}
- GET /bookings/occurrences (filter: company, member, location, resource)
- GET /assignments (filter: resource, membership)
- GET /locations (filter: name, isOpen, isPublic)
- GET /locations/{id}
- GET /floors (filter: location, name)
- GET /floors/{id}
- GET /amenities
- GET /amenities/{id}
"""

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Query

from db.engine import session_context
from db.models import (
    Resource, ResourceType, Booking, BookingOccurrence,
    Assignment, Location, Floor, Amenity,
)
from api.routes import paginated_query, apply_filters, get_single, count_query

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/space", tags=["Space"])


@router.get("/resources")
async def get_resources(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    type: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    floor: Optional[str] = Query(None),
    _id: Optional[str] = Query(None, alias="id"),
    name: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Get all resources with optional filtering and pagination."""
    filters = {}
    if type:
        filters["type"] = type
    if location:
        filters["location_id"] = location
    if floor:
        filters["floor_id"] = floor
    if _id:
        filters["_id"] = _id
    if name:
        filters["name"] = name

    with session_context() as session:
        return paginated_query(
            session, Resource,
            limit=limit or 100, offset=offset or 0,
            filters=apply_filters(Resource, filters),
        )


@router.get("/resources/count")
async def get_resources_count() -> Dict[str, Any]:
    """Get total count of resources."""
    with session_context() as session:
        return count_query(session, Resource)


@router.get("/resources/{resource_id}/status")
async def get_resource_status(resource_id: str) -> Dict[str, Any]:
    """Get resource status by ID."""
    with session_context() as session:
        record = session.query(Resource).filter(Resource._id == resource_id).first()
        if not record:
            return {"error": "Resource not found", "detail": f"Resource {resource_id} not found"}
        extra = record.extra or {}
        return {
            "_id": record._id,
            "status": extra.get("status", "available"),
            "ownStatus": extra.get("ownStatus", "available"),
        }


@router.get("/resources/{resource_id}")
async def get_resource(resource_id: str) -> Dict[str, Any]:
    """Get a single resource by ID."""
    with session_context() as session:
        return get_single(session, Resource, resource_id)


@router.get("/resource-types")
async def get_resource_types(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
) -> Dict[str, Any]:
    """Get all resource types with pagination."""
    with session_context() as session:
        return paginated_query(
            session, ResourceType,
            limit=limit or 100, offset=offset or 0,
            filters={},
        )


@router.get("/bookings")
async def get_bookings(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    resource: Optional[str] = Query(None),
    company: Optional[str] = Query(None),
    member: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Get all bookings with optional filtering and pagination."""
    filters = {}
    if resource:
        filters["resource_id"] = resource
    if company:
        filters["company_id"] = company
    if member:
        filters["member_id"] = member
    if location:
        filters["location_id"] = location

    with session_context() as session:
        return paginated_query(
            session, Booking,
            limit=limit or 100, offset=offset or 0,
            filters=apply_filters(Booking, filters),
        )


@router.get("/bookings/count")
async def get_bookings_count() -> Dict[str, Any]:
    """Get total count of bookings."""
    with session_context() as session:
        return count_query(session, Booking)


@router.get("/bookings/occurrences")
async def get_booking_occurrences(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    company: Optional[str] = Query(None),
    member: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    resource: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Get all booking occurrences with optional filtering and pagination."""
    filters = {}
    if company:
        filters["company_id"] = company
    if member:
        filters["member_id"] = member
    if location:
        filters["location_id"] = location
    if resource:
        filters["resource_id"] = resource

    with session_context() as session:
        return paginated_query(
            session, BookingOccurrence,
            limit=limit or 100, offset=offset or 0,
            filters=apply_filters(BookingOccurrence, filters),
        )


@router.get("/bookings/{booking_id}")
async def get_booking(booking_id: str) -> Dict[str, Any]:
    """Get a single booking by ID."""
    with session_context() as session:
        return get_single(session, Booking, booking_id)


@router.get("/assignments")
async def get_assignments(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    resource: Optional[str] = Query(None),
    membership: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Get all assignments with optional filtering and pagination."""
    filters = {}
    if resource:
        filters["resource_id"] = resource
    if membership:
        filters["membership_id"] = membership

    with session_context() as session:
        return paginated_query(
            session, Assignment,
            limit=limit or 100, offset=offset or 0,
            filters=apply_filters(Assignment, filters),
        )


@router.get("/locations")
async def get_locations(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    name: Optional[str] = Query(None),
    isOpen: Optional[bool] = Query(None),
    isPublic: Optional[bool] = Query(None),
) -> Dict[str, Any]:
    """Get all locations with optional filtering and pagination."""
    filters = {}
    if name:
        filters["name"] = name
    if isOpen is not None:
        filters["is_open"] = isOpen
    if isPublic is not None:
        filters["is_public"] = isPublic

    with session_context() as session:
        return paginated_query(
            session, Location,
            limit=limit or 100, offset=offset or 0,
            filters=apply_filters(Location, filters),
        )


@router.get("/locations/{location_id}")
async def get_location(location_id: str) -> Dict[str, Any]:
    """Get a single location by ID."""
    with session_context() as session:
        return get_single(session, Location, location_id)


@router.get("/floors")
async def get_floors(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    location: Optional[str] = Query(None),
    name: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Get all floors with optional filtering and pagination."""
    filters = {}
    if location:
        filters["location_id"] = location
    if name:
        filters["name"] = name

    with session_context() as session:
        return paginated_query(
            session, Floor,
            limit=limit or 100, offset=offset or 0,
            filters=apply_filters(Floor, filters),
        )


@router.get("/floors/{floor_id}")
async def get_floor(floor_id: str) -> Dict[str, Any]:
    """Get a single floor by ID."""
    with session_context() as session:
        return get_single(session, Floor, floor_id)


@router.get("/amenities")
async def get_amenities(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
) -> Dict[str, Any]:
    """Get all amenities with pagination."""
    with session_context() as session:
        return paginated_query(
            session, Amenity,
            limit=limit or 100, offset=offset or 0,
            filters={},
        )


@router.get("/amenities/{amenity_id}")
async def get_amenity(amenity_id: str) -> Dict[str, Any]:
    """Get a single amenity by ID."""
    with session_context() as session:
        return get_single(session, Amenity, amenity_id)
