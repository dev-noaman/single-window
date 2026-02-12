"""
Billing API routes for OfficeRnD API Offline Clone.

This module provides FastAPI routes for Billing API endpoints:
- GET /payments (filter: status, company, member) + GET /payments/{id}
- GET /charges (filter: status, payment) + GET /charges/{id}
- GET /credits (filter: company, member) + GET /credits/{id}
- GET /coins/stats
- GET /fees (filter: company, status, member, location, plan) + GET /fees/{id}
- GET /revenue-accounts
- GET /tax-rates
- GET /memberships (filter: company, status, member, plan) + GET /memberships/{id}
- GET /plans + GET /plans/{id}
- GET /resource-rates + GET /resource-rates/{id}
- GET /contracts (filter: company, location, status) + GET /contracts/{id}
- GET /benefits (filter: company, member) + GET /benefits/{id}
- GET /payment-details (filter: company, member)
"""

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Query

from db.engine import session_context
from db.models import (
    Payment, Charge, Credit, CoinsStats, Fee, RevenueAccount,
    TaxRate, Membership, Plan, ResourceRate, Contract, Benefit,
    PaymentDetail,
)
from api.routes import paginated_query, apply_filters, get_single, count_query

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/billing", tags=["Billing"])


@router.get("/payments")
async def get_payments(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    status: Optional[str] = Query(None),
    company: Optional[str] = Query(None),
    member: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Get all payments with optional filtering and pagination."""
    filters = {}
    if status:
        filters["status"] = status
    if company:
        filters["company_id"] = company
    if member:
        filters["member_id"] = member

    with session_context() as session:
        return paginated_query(
            session, Payment,
            limit=limit or 100, offset=offset or 0,
            filters=apply_filters(Payment, filters),
        )


@router.get("/payments/methods")
async def get_payment_methods() -> Dict[str, Any]:
    """Retrieve all payment methods."""
    with session_context() as session:
        from sqlalchemy import distinct, text
        rows = session.execute(
            text("SELECT DISTINCT extra->>'method' FROM payments WHERE extra->>'method' IS NOT NULL")
        ).scalars().all()
        return {"paymentMethods": sorted(rows) if rows else []}


@router.get("/payments/count")
async def get_payments_count() -> Dict[str, Any]:
    """Get total count of payments."""
    with session_context() as session:
        return count_query(session, Payment)


@router.get("/payments/{payment_id}")
async def get_payment(payment_id: str) -> Dict[str, Any]:
    """Get a single payment by ID."""
    with session_context() as session:
        return get_single(session, Payment, payment_id)


@router.get("/charges")
async def get_charges(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    status: Optional[str] = Query(None),
    payment: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Get all charges with optional filtering and pagination."""
    filters = {}
    if status:
        filters["status"] = status
    if payment:
        filters["payment_id"] = payment

    with session_context() as session:
        return paginated_query(
            session, Charge,
            limit=limit or 100, offset=offset or 0,
            filters=apply_filters(Charge, filters),
        )


@router.get("/charges/{charge_id}")
async def get_charge(charge_id: str) -> Dict[str, Any]:
    """Get a single charge by ID."""
    with session_context() as session:
        return get_single(session, Charge, charge_id)


@router.get("/credits")
async def get_credits(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    company: Optional[str] = Query(None),
    member: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Get all credits with optional filtering and pagination."""
    filters = {}
    if company:
        filters["company_id"] = company
    if member:
        filters["member_id"] = member

    with session_context() as session:
        return paginated_query(
            session, Credit,
            limit=limit or 100, offset=offset or 0,
            filters=apply_filters(Credit, filters),
        )


@router.get("/credits/{credit_id}")
async def get_credit(credit_id: str) -> Dict[str, Any]:
    """Get a single credit by ID."""
    with session_context() as session:
        return get_single(session, Credit, credit_id)


@router.get("/coins/stats")
async def get_coins_stats(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
) -> Dict[str, Any]:
    """Get all coins stats with pagination."""
    with session_context() as session:
        return paginated_query(
            session, CoinsStats,
            limit=limit or 100, offset=offset or 0,
            filters={},
        )


@router.get("/fees")
async def get_fees(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    company: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    member: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    plan: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Get all fees with optional filtering and pagination."""
    filters = {}
    if company:
        filters["company_id"] = company
    if status:
        filters["status"] = status
    if member:
        filters["member_id"] = member
    if location:
        filters["location_id"] = location
    if plan:
        filters["plan_type"] = plan

    with session_context() as session:
        return paginated_query(
            session, Fee,
            limit=limit or 100, offset=offset or 0,
            filters=apply_filters(Fee, filters),
        )


@router.get("/fees/count")
async def get_fees_count() -> Dict[str, Any]:
    """Get total count of fees."""
    with session_context() as session:
        return count_query(session, Fee)


@router.get("/fees/{fee_id}")
async def get_fee(fee_id: str) -> Dict[str, Any]:
    """Get a single fee by ID."""
    with session_context() as session:
        return get_single(session, Fee, fee_id)


@router.get("/revenue-accounts")
async def get_revenue_accounts(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
) -> Dict[str, Any]:
    """Get all revenue accounts with pagination."""
    with session_context() as session:
        return paginated_query(
            session, RevenueAccount,
            limit=limit or 100, offset=offset or 0,
            filters={},
        )


@router.get("/tax-rates")
async def get_tax_rates(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
) -> Dict[str, Any]:
    """Get all tax rates with pagination."""
    with session_context() as session:
        return paginated_query(
            session, TaxRate,
            limit=limit or 100, offset=offset or 0,
            filters={},
        )


@router.get("/memberships")
async def get_memberships(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    company: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    member: Optional[str] = Query(None),
    plan: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Get all memberships with optional filtering and pagination."""
    filters = {}
    if company:
        filters["company_id"] = company
    if status:
        filters["status"] = status
    if member:
        filters["member_id"] = member
    if plan:
        filters["plan_id"] = plan

    with session_context() as session:
        return paginated_query(
            session, Membership,
            limit=limit or 100, offset=offset or 0,
            filters=apply_filters(Membership, filters),
        )


@router.get("/memberships/count")
async def get_memberships_count() -> Dict[str, Any]:
    """Get total count of memberships."""
    with session_context() as session:
        return count_query(session, Membership)


@router.get("/memberships/{membership_id}")
async def get_membership(membership_id: str) -> Dict[str, Any]:
    """Get a single membership by ID."""
    with session_context() as session:
        return get_single(session, Membership, membership_id)


@router.get("/plans")
async def get_plans(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
) -> Dict[str, Any]:
    """Get all plans with pagination."""
    with session_context() as session:
        return paginated_query(
            session, Plan,
            limit=limit or 100, offset=offset or 0,
            filters={},
        )


@router.get("/plans/count")
async def get_plans_count() -> Dict[str, Any]:
    """Get total count of plans."""
    with session_context() as session:
        return count_query(session, Plan)


@router.get("/plans/{plan_id}")
async def get_plan(plan_id: str) -> Dict[str, Any]:
    """Get a single plan by ID."""
    with session_context() as session:
        return get_single(session, Plan, plan_id)


@router.get("/resource-rates")
async def get_resource_rates(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
) -> Dict[str, Any]:
    """Get all resource rates with pagination."""
    with session_context() as session:
        return paginated_query(
            session, ResourceRate,
            limit=limit or 100, offset=offset or 0,
            filters={},
        )


@router.get("/resource-rates/count")
async def get_resource_rates_count() -> Dict[str, Any]:
    """Get total count of resource rates."""
    with session_context() as session:
        return count_query(session, ResourceRate)


@router.get("/resource-rates/{rate_id}")
async def get_resource_rate(rate_id: str) -> Dict[str, Any]:
    """Get a single resource rate by ID."""
    with session_context() as session:
        return get_single(session, ResourceRate, rate_id)


@router.get("/contracts")
async def get_contracts(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    company: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Get all contracts with optional filtering and pagination."""
    filters = {}
    if company:
        filters["company_id"] = company
    if location:
        filters["location_id"] = location
    if status:
        filters["status"] = status

    with session_context() as session:
        return paginated_query(
            session, Contract,
            limit=limit or 100, offset=offset or 0,
            filters=apply_filters(Contract, filters),
        )


@router.get("/contracts/count")
async def get_contracts_count() -> Dict[str, Any]:
    """Get total count of contracts."""
    with session_context() as session:
        return count_query(session, Contract)


@router.get("/contracts/{contract_id}")
async def get_contract(contract_id: str) -> Dict[str, Any]:
    """Get a single contract by ID."""
    with session_context() as session:
        return get_single(session, Contract, contract_id)


@router.get("/benefits")
async def get_benefits(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    company: Optional[str] = Query(None),
    member: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Get all benefits with optional filtering and pagination."""
    filters = {}
    if company:
        filters["company_id"] = company
    if member:
        filters["member_id"] = member

    with session_context() as session:
        return paginated_query(
            session, Benefit,
            limit=limit or 100, offset=offset or 0,
            filters=apply_filters(Benefit, filters),
        )


@router.get("/benefits/count")
async def get_benefits_count() -> Dict[str, Any]:
    """Get total count of benefits."""
    with session_context() as session:
        return count_query(session, Benefit)


@router.get("/benefits/{benefit_id}")
async def get_benefit(benefit_id: str) -> Dict[str, Any]:
    """Get a single benefit by ID."""
    with session_context() as session:
        return get_single(session, Benefit, benefit_id)


@router.get("/payment-details")
async def get_payment_details(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    company: Optional[str] = Query(None),
    member: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Get all payment details with optional filtering and pagination."""
    filters = {}
    if company:
        filters["company_id"] = company
    if member:
        filters["member_id"] = member

    with session_context() as session:
        return paginated_query(
            session, PaymentDetail,
            limit=limit or 100, offset=offset or 0,
            filters=apply_filters(PaymentDetail, filters),
        )
