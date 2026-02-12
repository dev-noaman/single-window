"""
Community API routes for OfficeRnD API Offline Clone.

This module provides FastAPI routes for Community API endpoints:
- GET /members (filter: company, status, _id, name, email, location)
- GET /members/{id}
- GET /companies (filter: status, _id, name, location)
- GET /companies/{id}
- GET /visitors (filter: member, company, type, location)
- GET /visitors/{id}
- GET /opportunities (filter: company, member, status)
- GET /opportunities/{id}
- GET /passes (filter: company, member)
- GET /passes/{id}
"""

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Query

from db.engine import session_context
from db.models import Member, Company, Visitor, Opportunity, Pass
from api.routes import paginated_query, apply_filters, get_single, count_query

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/community", tags=["Community"])


@router.get("/members")
async def get_members(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    company: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    _id: Optional[str] = Query(None, alias="id"),
    name: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Get all members with optional filtering and pagination."""
    filters = {}
    if company:
        filters["company_id"] = company
    if status:
        filters["status"] = status
    if _id:
        filters["_id"] = _id
    if name:
        filters["name"] = name
    if email:
        filters["email"] = email
    if location:
        filters["location_id"] = location

    with session_context() as session:
        return paginated_query(
            session, Member,
            limit=limit or 100, offset=offset or 0,
            filters=apply_filters(Member, filters),
        )


@router.get("/members/count")
async def get_members_count(
    countBy: Optional[str] = Query(None, alias="$countBy"),
) -> Dict[str, Any]:
    """Get total count of members, optionally grouped by a field."""
    with session_context() as session:
        return count_query(session, Member, count_by=countBy)


@router.get("/members/{member_id}")
async def get_member(member_id: str) -> Dict[str, Any]:
    """Get a single member by ID."""
    with session_context() as session:
        return get_single(session, Member, member_id)


@router.get("/companies")
async def get_companies(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    status: Optional[str] = Query(None),
    _id: Optional[str] = Query(None, alias="id"),
    name: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Get all companies with optional filtering and pagination."""
    filters = {}
    if status:
        filters["status"] = status
    if _id:
        filters["_id"] = _id
    if name:
        filters["name"] = name
    if location:
        filters["location_id"] = location

    with session_context() as session:
        return paginated_query(
            session, Company,
            limit=limit or 100, offset=offset or 0,
            filters=apply_filters(Company, filters),
        )


@router.get("/companies/{company_id}")
async def get_company(company_id: str) -> Dict[str, Any]:
    """Get a single company by ID."""
    with session_context() as session:
        return get_single(session, Company, company_id)


@router.get("/visitors")
async def get_visitors(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    member: Optional[str] = Query(None),
    company: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Get all visitors with optional filtering and pagination."""
    filters = {}
    if member:
        filters["member_id"] = member
    if company:
        filters["company_id"] = company
    if type:
        filters["type"] = type
    if location:
        filters["location_id"] = location

    with session_context() as session:
        return paginated_query(
            session, Visitor,
            limit=limit or 100, offset=offset or 0,
            filters=apply_filters(Visitor, filters),
        )


@router.get("/visitors/{visitor_id}")
async def get_visitor(visitor_id: str) -> Dict[str, Any]:
    """Get a single visitor by ID."""
    with session_context() as session:
        return get_single(session, Visitor, visitor_id)


@router.get("/opportunities")
async def get_opportunities(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    company: Optional[str] = Query(None),
    member: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Get all opportunities with optional filtering and pagination."""
    filters = {}
    if company:
        filters["company_id"] = company
    if member:
        filters["member_id"] = member
    if status:
        filters["status"] = status

    with session_context() as session:
        return paginated_query(
            session, Opportunity,
            limit=limit or 100, offset=offset or 0,
            filters=apply_filters(Opportunity, filters),
        )


@router.get("/opportunities/count")
async def get_opportunities_count() -> Dict[str, Any]:
    """Get total count of opportunities."""
    with session_context() as session:
        return count_query(session, Opportunity)


@router.get("/opportunities/{opportunity_id}")
async def get_opportunity(opportunity_id: str) -> Dict[str, Any]:
    """Get a single opportunity by ID."""
    with session_context() as session:
        return get_single(session, Opportunity, opportunity_id)


@router.get("/passes")
async def get_passes(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    company: Optional[str] = Query(None),
    member: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Get all passes with optional filtering and pagination."""
    filters = {}
    if company:
        filters["company_id"] = company
    if member:
        filters["member_id"] = member

    with session_context() as session:
        return paginated_query(
            session, Pass,
            limit=limit or 100, offset=offset or 0,
            filters=apply_filters(Pass, filters),
        )


@router.get("/passes/{pass_id}")
async def get_pass(pass_id: str) -> Dict[str, Any]:
    """Get a single pass by ID."""
    with session_context() as session:
        return get_single(session, Pass, pass_id)
