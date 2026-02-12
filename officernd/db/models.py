"""
SQLAlchemy ORM models for OfficeRnD API Offline Clone.

ALL columns are nullable except _id (primary key), extra (JSONB), and synced_at.
This ensures no API response is rejected due to NOT NULL constraints.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, DateTime, Float, Integer, Index, Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


# ============================================================================
# Community API Models
# ============================================================================

class Member(Base):
    __tablename__ = "members"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    email: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    company_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_billing_person: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    is_contact_person: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    modified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    __table_args__ = (
        Index("ix_members_company_id", "company_id"),
        Index("ix_members_location_id", "location_id"),
        Index("ix_members_status", "status"),
    )


class Company(Base):
    __tablename__ = "companies"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    email: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_date: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    has_active_members_allowance: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    modified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    modified_by: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    __table_args__ = (
        Index("ix_companies_location_id", "location_id"),
        Index("ix_companies_status", "status"),
    )


class Visitor(Base):
    __tablename__ = "visitors"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    email: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    member_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    company_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class Opportunity(Base):
    __tablename__ = "opportunities"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    company_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    member_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    probability: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    start_date: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    deal_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    members_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    location_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    modified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


# ============================================================================
# Space API Models
# ============================================================================

class Resource(Base):
    __tablename__ = "resources"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    floor_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    deposit: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    area: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    privacy: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    modified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    __table_args__ = (
        Index("ix_resources_location_id", "location_id"),
        Index("ix_resources_type", "type"),
        Index("ix_resources_floor_id", "floor_id"),
    )


class ResourceType(Base):
    __tablename__ = "resource_types"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    booking_mode: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    checkin_mode: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    can_book: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    can_assign: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    is_primary: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    is_hierarchical: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class Booking(Base):
    __tablename__ = "bookings"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    timezone: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    location_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    company_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    member_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resource_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reference: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_free: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    is_accounted: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    is_cancelled: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    is_tentative: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    series_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    series_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    source: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    modified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    __table_args__ = (
        Index("ix_bookings_resource_id", "resource_id"),
        Index("ix_bookings_company_id", "company_id"),
        Index("ix_bookings_start_end", "start", "end"),
    )


class BookingOccurrence(Base):
    __tablename__ = "booking_occurrences"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    booking_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timezone: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    location_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    company_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    member_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resource_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reference: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_accounted: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    is_cancelled: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    is_tentative: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    source: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    modified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    __table_args__ = (
        Index("ix_booking_occurrences_booking_id", "booking_id"),
        Index("ix_booking_occurrences_resource_id", "resource_id"),
        Index("ix_booking_occurrences_start_end", "start", "end"),
    )


class Assignment(Base):
    __tablename__ = "assignments"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    resource_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    membership_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_date: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    end_date: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class Location(Base):
    __tablename__ = "locations"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timezone: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_open: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    is_public: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    image: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class Floor(Base):
    __tablename__ = "floors"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    floor: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    area: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_open: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    modified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


# ============================================================================
# Collaboration API Models
# ============================================================================

class Post(Base):
    __tablename__ = "posts"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    company_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    member_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    modified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class Event(Base):
    __tablename__ = "events"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    modified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class Ticket(Base):
    __tablename__ = "tickets"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    severity: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    priority: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    company_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    member_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    subject: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    assigned_to: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    __table_args__ = (
        Index("ix_tickets_company_id", "company_id"),
        Index("ix_tickets_status", "status"),
    )


class TicketOption(Base):
    __tablename__ = "ticket_options"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    category: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    label: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


# ============================================================================
# Billing API Models
# ============================================================================

class Payment(Base):
    __tablename__ = "payments"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    amount: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    date: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    company_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    member_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reference: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    modified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    __table_args__ = (
        Index("ix_payments_status", "status"),
        Index("ix_payments_date", "date"),
        Index("ix_payments_company_id", "company_id"),
    )


class Charge(Base):
    __tablename__ = "charges"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    amount: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    date: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    payment_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reference: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    company_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    modified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    __table_args__ = (
        Index("ix_charges_payment_id", "payment_id"),
    )


class Credit(Base):
    __tablename__ = "credits"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    company_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    member_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    membership_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    interval_length: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_date: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    end_date: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    valid_for: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class CoinsStats(Base):
    __tablename__ = "coins_stats"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    company_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    member_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class Fee(Base):
    __tablename__ = "fees"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    quantity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    company_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    member_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    plan_type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    issue_date: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_refundable: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    is_personal: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    modified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    __table_args__ = (
        Index("ix_fees_company_id", "company_id"),
        Index("ix_fees_member_id", "member_id"),
        Index("ix_fees_status", "status"),
    )


class RevenueAccount(Base):
    __tablename__ = "revenue_accounts"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    default_for: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class TaxRate(Base):
    __tablename__ = "tax_rates"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class Membership(Base):
    __tablename__ = "memberships"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_personal: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    calculated_status: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    plan_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    company_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    member_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_date: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    end_date: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    interval_length: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    interval_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_locked: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    price: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    modified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    __table_args__ = (
        Index("ix_memberships_company_id", "company_id"),
        Index("ix_memberships_member_id", "member_id"),
        Index("ix_memberships_plan_id", "plan_id"),
        Index("ix_memberships_status", "status"),
    )


class Plan(Base):
    __tablename__ = "plans"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    deposit: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    interval_length: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    interval_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    should_prorate: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    use_coins: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    for_members: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    for_team_members: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    for_non_members: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class ResourceRate(Base):
    __tablename__ = "resource_rates"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    interval_length: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    interval_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    price: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    should_prorate: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    use_coins: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    revenue_account_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class Contract(Base):
    __tablename__ = "contracts"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    number: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    company_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    member_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    stage: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_date: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    end_date: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    total: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    modified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    __table_args__ = (
        Index("ix_contracts_company_id", "company_id"),
        Index("ix_contracts_status", "status"),
    )


# ============================================================================
# Visits & Check-ins Models
# ============================================================================

class Visit(Base):
    __tablename__ = "visits"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    member_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    visitor_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    company_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reception_flow_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class Checkin(Base):
    __tablename__ = "checkins"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    location_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    company_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    member_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    booking_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    pass_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resource_type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


# ============================================================================
# Webhooks & Settings Models
# ============================================================================

class Webhook(Base):
    __tablename__ = "webhooks"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_enabled: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    secret: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


# ============================================================================
# New Endpoint Models (from reference docs)
# ============================================================================

class Amenity(Base):
    __tablename__ = "amenities"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class Benefit(Base):
    __tablename__ = "benefits"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    company_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    member_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class BillingSetting(Base):
    __tablename__ = "billing_settings"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class BusinessHour(Base):
    __tablename__ = "business_hours"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    location_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    day_of_week: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class CustomProperty(Base):
    __tablename__ = "custom_properties"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    entity_type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class OpportunityStatus(Base):
    __tablename__ = "opportunity_statuses"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    order: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class ReceptionFlow(Base):
    __tablename__ = "reception_flows"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class SecondaryCurrency(Base):
    __tablename__ = "secondary_currencies"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    code: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class PaymentDetail(Base):
    __tablename__ = "payment_details"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    company_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    member_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class Pass(Base):
    __tablename__ = "passes"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    company_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    member_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    plan_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_date: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    end_date: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    used_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class Organization(Base):
    __tablename__ = "organizations"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    slug: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class Integration(Base):
    __tablename__ = "integrations"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    user: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


# ============================================================================
# Dependent Endpoint Models (require parent IDs to fetch)
# ============================================================================

class PaymentDocument(Base):
    __tablename__ = "payment_documents"
    _id: Mapped[str] = mapped_column(Text, primary_key=True)
    payment_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    __table_args__ = (
        Index("ix_payment_documents_payment_id", "payment_id"),
    )


# ============================================================================
# Internal Sync Tracking Models
# ============================================================================

class SyncJob(Base):
    __tablename__ = "sync_jobs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    endpoint: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_cursor: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    records_fetched: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=0)
    records_upserted: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, default=datetime.utcnow)
    __table_args__ = (
        Index("ix_sync_jobs_endpoint_status", "endpoint", "status"),
    )


class SyncJobCompany(Base):
    __tablename__ = "sync_jobs_company"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    company_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    endpoints_completed: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=0)
    endpoints_failed: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=0)
    endpoints_skipped: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=0)
    total_records_fetched: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=0)
    total_records_upserted: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, default=datetime.utcnow)
    __table_args__ = (
        Index("ix_sync_jobs_company_id_status", "company_id", "status"),
        Index("ix_sync_jobs_company_status", "status"),
    )
