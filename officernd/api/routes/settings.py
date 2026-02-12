"""
Settings API routes for OfficeRnD API Offline Clone.

This module provides FastAPI routes for Settings API endpoints:
- GET /webhooks
- GET /billing-settings
- GET /business-hours
- GET /custom-properties
- GET /opportunity-statuses
- GET /reception-flows
- GET /secondary-currencies + GET /secondary-currencies/{id}
- GET /organizations
"""

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Query

from db.engine import session_context
from db.models import (
    Webhook, BillingSetting, BusinessHour, CustomProperty,
    OpportunityStatus, ReceptionFlow, SecondaryCurrency, Organization,
    Integration,
)
from api.routes import paginated_query, apply_filters, get_single

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("/webhooks")
async def get_webhooks(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
) -> Dict[str, Any]:
    """Get all webhooks with pagination."""
    with session_context() as session:
        return paginated_query(
            session, Webhook,
            limit=limit or 100, offset=offset or 0,
            filters={},
        )


@router.get("/billing-settings")
async def get_billing_settings(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
) -> Dict[str, Any]:
    """Get billing settings."""
    with session_context() as session:
        return paginated_query(
            session, BillingSetting,
            limit=limit or 100, offset=offset or 0,
            filters={},
        )


@router.get("/business-hours")
async def get_business_hours(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
) -> Dict[str, Any]:
    """Get all business hours with pagination."""
    with session_context() as session:
        return paginated_query(
            session, BusinessHour,
            limit=limit or 100, offset=offset or 0,
            filters={},
        )


@router.get("/custom-properties")
async def get_custom_properties(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
) -> Dict[str, Any]:
    """Get all custom properties with pagination."""
    with session_context() as session:
        return paginated_query(
            session, CustomProperty,
            limit=limit or 100, offset=offset or 0,
            filters={},
        )


@router.get("/opportunity-statuses")
async def get_opportunity_statuses(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
) -> Dict[str, Any]:
    """Get all opportunity statuses with pagination."""
    with session_context() as session:
        return paginated_query(
            session, OpportunityStatus,
            limit=limit or 100, offset=offset or 0,
            filters={},
        )


@router.get("/reception-flows")
async def get_reception_flows(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
) -> Dict[str, Any]:
    """Get all reception flows with pagination."""
    with session_context() as session:
        return paginated_query(
            session, ReceptionFlow,
            limit=limit or 100, offset=offset or 0,
            filters={},
        )


@router.get("/secondary-currencies")
async def get_secondary_currencies(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
) -> Dict[str, Any]:
    """Get all secondary currencies with pagination."""
    with session_context() as session:
        return paginated_query(
            session, SecondaryCurrency,
            limit=limit or 100, offset=offset or 0,
            filters={},
        )


@router.get("/secondary-currencies/{currency_id}")
async def get_secondary_currency(currency_id: str) -> Dict[str, Any]:
    """Get a single secondary currency by ID."""
    with session_context() as session:
        return get_single(session, SecondaryCurrency, currency_id)


@router.get("/organizations")
async def get_organizations(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
) -> Dict[str, Any]:
    """Get all organizations with pagination."""
    with session_context() as session:
        return paginated_query(
            session, Organization,
            limit=limit or 100, offset=offset or 0,
            filters={},
        )


@router.get("/integrations/{integration_id}")
async def get_integration(integration_id: str) -> Dict[str, Any]:
    """Get a single integration by ID."""
    with session_context() as session:
        return get_single(session, Integration, integration_id)
