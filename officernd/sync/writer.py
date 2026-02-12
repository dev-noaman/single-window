"""Database upsert writer with batch support and endpoint-to-model mapping."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Type

from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import insert as pg_insert

from db.engine import session_context
from db.models import (
    Amenity, Assignment, Base, Benefit, BillingSetting, Booking,
    BookingOccurrence, BusinessHour, Charge, Checkin, CoinsStats, Company,
    Contract, Credit, CustomProperty, Event, Fee, Floor, Location, Member,
    Membership, Opportunity, OpportunityStatus, Organization, Pass, Payment,
    PaymentDetail, PaymentDocument, Plan, Post, ReceptionFlow, Resource,
    ResourceRate, ResourceType, RevenueAccount, SecondaryCurrency, TaxRate,
    Ticket, TicketOption, Visit, Visitor, Webhook,
)

logger = logging.getLogger(__name__)

BATCH_SIZE = 100

# Endpoint name -> SQLAlchemy model class
ENDPOINT_MODEL_MAP: Dict[str, Type[Base]] = {
    "members": Member,
    "companies": Company,
    "visitors": Visitor,
    "opportunities": Opportunity,
    "resources": Resource,
    "resource-types": ResourceType,
    "bookings": Booking,
    "bookings/occurrences": BookingOccurrence,
    "assignments": Assignment,
    "locations": Location,
    "floors": Floor,
    "posts": Post,
    "events": Event,
    "tickets": Ticket,
    "ticket-options": TicketOption,
    "payments": Payment,
    "charges": Charge,
    "credits": Credit,
    "coins/stats": CoinsStats,
    "fees": Fee,
    "revenue-accounts": RevenueAccount,
    "tax-rates": TaxRate,
    "memberships": Membership,
    "plans": Plan,
    "resource-rates": ResourceRate,
    "contracts": Contract,
    "visits": Visit,
    "checkins": Checkin,
    "webhooks": Webhook,
    "payment-documents": PaymentDocument,
    "amenities": Amenity,
    "benefits": Benefit,
    "billing-settings": BillingSetting,
    "business-hours": BusinessHour,
    "custom-properties": CustomProperty,
    "opportunity-statuses": OpportunityStatus,
    "reception-flows": ReceptionFlow,
    "secondary-currencies": SecondaryCurrency,
    "payment-details": PaymentDetail,
    "passes": Pass,
    "organizations": Organization,
}


def get_model_for_endpoint(endpoint: str) -> Optional[Type[Base]]:
    """Get the SQLAlchemy model class for an endpoint name."""
    # Try direct match first
    if endpoint in ENDPOINT_MODEL_MAP:
        return ENDPOINT_MODEL_MAP[endpoint]

    # Handle dependent endpoints like "payments/{id}/documents"
    if "/documents" in endpoint:
        return PaymentDocument

    # Handle query-param endpoints like "assignments?membership=xxx"
    base = endpoint.split("?")[0]
    return ENDPOINT_MODEL_MAP.get(base)


def upsert_records(
    endpoint: str,
    records: List[Dict[str, Any]],
    parent_id_field: Optional[str] = None,
    parent_id_value: Optional[str] = None,
) -> int:
    """
    Upsert records into the database using ON CONFLICT DO UPDATE.

    Processes in batches of BATCH_SIZE. Falls back to row-by-row on batch failure.
    Returns count of upserted records.
    """
    model = get_model_for_endpoint(endpoint)
    if not model:
        logger.warning(f"No model found for endpoint: {endpoint}")
        return 0

    if not records:
        return 0

    # Get model column names for filtering record fields
    mapper = inspect(model)
    column_names = {c.key for c in mapper.columns}

    total_upserted = 0

    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i : i + BATCH_SIZE]
        try:
            total_upserted += _upsert_batch(model, column_names, batch, parent_id_field, parent_id_value)
        except Exception as e:
            logger.warning(f"Batch upsert failed for {endpoint}, falling back to row-by-row: {e}")
            for record in batch:
                try:
                    total_upserted += _upsert_batch(model, column_names, [record], parent_id_field, parent_id_value)
                except Exception as row_err:
                    logger.error(f"Row upsert failed for {endpoint} _id={record.get('_id')}: {row_err}")

    return total_upserted


def _upsert_batch(
    model: Type[Base],
    column_names: set,
    batch: List[Dict[str, Any]],
    parent_id_field: Optional[str],
    parent_id_value: Optional[str],
) -> int:
    """Upsert a single batch of records using PostgreSQL ON CONFLICT DO UPDATE."""
    rows = []
    now = datetime.now(timezone.utc)

    for record in batch:
        row = {"extra": record, "synced_at": now}

        # Extract known columns from the record
        for key, value in record.items():
            if key in column_names and key not in ("extra", "synced_at"):
                row[key] = value

        # Add parent ID if applicable (e.g. payment_id for payment documents)
        if parent_id_field and parent_id_value:
            row[parent_id_field] = parent_id_value

        # Must have _id
        if "_id" not in row:
            continue

        rows.append(row)

    if not rows:
        return 0

    # Normalize: all rows must have the same keys for batch insert
    all_keys = set()
    for r in rows:
        all_keys.update(r.keys())
    for r in rows:
        for k in all_keys:
            if k not in r:
                r[k] = None

    with session_context() as session:
        stmt = pg_insert(model).values(rows)

        # Build update dict for ON CONFLICT - only columns present in the data
        update_cols = {c.name: stmt.excluded[c.name] for c in model.__table__.columns if c.name != "_id" and c.name in all_keys}

        stmt = stmt.on_conflict_do_update(
            index_elements=["_id"],
            set_=update_cols,
        )

        session.execute(stmt)

    return len(rows)
