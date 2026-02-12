"""Initial schema with all OfficeRnD API models

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-02-08 13:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create Community API tables
    op.create_table(
        'members',
        sa.Column('_id', sa.Text(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('email', sa.Text(), nullable=True),
        sa.Column('phone', sa.Text(), nullable=True),
        sa.Column('status', sa.Text(), nullable=False),
        sa.Column('company_id', sa.Text(), nullable=True),
        sa.Column('location_id', sa.Text(), nullable=True),
        sa.Column('is_billing_person', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_contact_person', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('modified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('extra', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('synced_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('_id')
    )
    op.create_index('ix_members_company_id', 'members', ['company_id'])
    op.create_index('ix_members_location_id', 'members', ['location_id'])
    op.create_index('ix_members_status', 'members', ['status'])

    op.create_table(
        'companies',
        sa.Column('_id', sa.Text(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('email', sa.Text(), nullable=True),
        sa.Column('status', sa.Text(), nullable=False),
        sa.Column('location_id', sa.Text(), nullable=True),
        sa.Column('start_date', sa.Text(), nullable=True),
        sa.Column('has_active_members_allowance', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('modified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('modified_by', sa.Text(), nullable=True),
        sa.Column('extra', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('synced_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('_id')
    )
    op.create_index('ix_companies_location_id', 'companies', ['location_id'])
    op.create_index('ix_companies_status', 'companies', ['status'])

    op.create_table(
        'visitors',
        sa.Column('_id', sa.Text(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('email', sa.Text(), nullable=True),
        sa.Column('member_id', sa.Text(), nullable=True),
        sa.Column('type', sa.Text(), nullable=False),
        sa.Column('extra', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('synced_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('_id')
    )

    op.create_table(
        'opportunities',
        sa.Column('_id', sa.Text(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('company_id', sa.Text(), nullable=True),
        sa.Column('member_id', sa.Text(), nullable=True),
        sa.Column('status', sa.Text(), nullable=True),
        sa.Column('probability', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.Text(), nullable=True),
        sa.Column('deal_size', sa.Integer(), nullable=False),
        sa.Column('extra', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('synced_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('_id')
    )

    # Create Space API tables
    op.create_table(
        'resources',
        sa.Column('_id', sa.Text(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('type', sa.Text(), nullable=False),
        sa.Column('location_id', sa.Text(), nullable=True),
        sa.Column('floor_id', sa.Text(), nullable=True),
        sa.Column('price', sa.Integer(), nullable=False),
        sa.Column('deposit', sa.Integer(), nullable=False),
        sa.Column('size', sa.Integer(), nullable=False),
        sa.Column('area', sa.Float(), nullable=True),
        sa.Column('privacy', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('modified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('extra', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('synced_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('_id')
    )
    op.create_index('ix_resources_location_id', 'resources', ['location_id'])
    op.create_index('ix_resources_type', 'resources', ['type'])
    op.create_index('ix_resources_floor_id', 'resources', ['floor_id'])

    op.create_table(
        'resource_types',
        sa.Column('_id', sa.Text(), nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('type', sa.Text(), nullable=False),
        sa.Column('booking_mode', sa.Text(), nullable=False),
        sa.Column('checkin_mode', sa.Text(), nullable=False),
        sa.Column('icon', sa.Text(), nullable=True),
        sa.Column('can_book', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('can_assign', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_hierarchical', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('extra', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('synced_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('_id')
    )

    op.create_table(
        'bookings',
        sa.Column('_id', sa.Text(), nullable=False),
        sa.Column('timezone', sa.Text(), nullable=False),
        sa.Column('start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('location_id', sa.Text(), nullable=True),
        sa.Column('company_id', sa.Text(), nullable=True),
        sa.Column('member_id', sa.Text(), nullable=True),
        sa.Column('resource_id', sa.Text(), nullable=False),
        sa.Column('reference', sa.Text(), nullable=True),
        sa.Column('is_free', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_accounted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('source', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('modified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('extra', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('synced_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('_id')
    )
    op.create_index('ix_bookings_resource_id', 'bookings', ['resource_id'])
    op.create_index('ix_bookings_company_id', 'bookings', ['company_id'])
    op.create_index('ix_bookings_start_end', 'bookings', ['start', 'end'])

    op.create_table(
        'booking_occurrences',
        sa.Column('_id', sa.Text(), nullable=False),
        sa.Column('booking_id', sa.Text(), nullable=False),
        sa.Column('timezone', sa.Text(), nullable=False),
        sa.Column('start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('location_id', sa.Text(), nullable=True),
        sa.Column('company_id', sa.Text(), nullable=True),
        sa.Column('member_id', sa.Text(), nullable=True),
        sa.Column('resource_id', sa.Text(), nullable=False),
        sa.Column('reference', sa.Text(), nullable=True),
        sa.Column('is_accounted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('source', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('modified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('extra', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('synced_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('_id')
    )
    op.create_index('ix_booking_occurrences_booking_id', 'booking_occurrences', ['booking_id'])
    op.create_index('ix_booking_occurrences_resource_id', 'booking_occurrences', ['resource_id'])
    op.create_index('ix_booking_occurrences_start_end', 'booking_occurrences', ['start', 'end'])

    op.create_table(
        'assignments',
        sa.Column('_id', sa.Text(), nullable=False),
        sa.Column('resource_id', sa.Text(), nullable=False),
        sa.Column('membership_id', sa.Text(), nullable=False),
        sa.Column('start_date', sa.Text(), nullable=True),
        sa.Column('end_date', sa.Text(), nullable=True),
        sa.Column('extra', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('synced_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('_id')
    )

    op.create_table(
        'locations',
        sa.Column('_id', sa.Text(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('timezone', sa.Text(), nullable=False),
        sa.Column('is_open', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('image', sa.Text(), nullable=True),
        sa.Column('extra', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('synced_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('_id')
    )

    op.create_table(
        'floors',
        sa.Column('_id', sa.Text(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('floor', sa.Text(), nullable=False),
        sa.Column('location_id', sa.Text(), nullable=False),
        sa.Column('area', sa.Integer(), nullable=False),
        sa.Column('is_open', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('modified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('extra', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('synced_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('_id')
    )

    # Create Collaboration API tables
    op.create_table(
        'posts',
        sa.Column('_id', sa.Text(), nullable=False),
        sa.Column('extra', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('synced_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('_id')
    )

    op.create_table(
        'events',
        sa.Column('_id', sa.Text(), nullable=False),
        sa.Column('extra', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('synced_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('_id')
    )

    op.create_table(
        'tickets',
        sa.Column('_id', sa.Text(), nullable=False),
        sa.Column('type', sa.Text(), nullable=False),
        sa.Column('severity', sa.Text(), nullable=False),
        sa.Column('priority', sa.Text(), nullable=False),
        sa.Column('status', sa.Text(), nullable=False),
        sa.Column('company_id', sa.Text(), nullable=False),
        sa.Column('member_id', sa.Text(), nullable=False),
        sa.Column('location_id', sa.Text(), nullable=True),
        sa.Column('subject', sa.Text(), nullable=False),
        sa.Column('assigned_to', sa.Text(), nullable=True),
        sa.Column('extra', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('synced_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('_id')
    )
    op.create_index('ix_tickets_company_id', 'tickets', ['company_id'])
    op.create_index('ix_tickets_status', 'tickets', ['status'])

    op.create_table(
        'ticket_options',
        sa.Column('_id', sa.Text(), nullable=False),
        sa.Column('category', sa.Text(), nullable=False),
        sa.Column('label', sa.Text(), nullable=False),
        sa.Column('extra', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('synced_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('_id')
    )

    # Create Billing API tables
    op.create_table(
        'payments',
        sa.Column('_id', sa.Text(), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('date', sa.Text(), nullable=False),
        sa.Column('status', sa.Text(), nullable=False),
        sa.Column('source', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('modified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('extra', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('synced_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('_id')
    )
    op.create_index('ix_payments_status', 'payments', ['status'])
    op.create_index('ix_payments_date', 'payments', ['date'])

    op.create_table(
        'charges',
        sa.Column('_id', sa.Text(), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('date', sa.Text(), nullable=False),
        sa.Column('status', sa.Text(), nullable=False),
        sa.Column('source', sa.Text(), nullable=False),
        sa.Column('payment_id', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('modified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('extra', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('synced_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('_id')
    )
    op.create_index('ix_charges_payment_id', 'charges', ['payment_id'])

    op.create_table(
        'credits',
        sa.Column('_id', sa.Text(), nullable=False),
        sa.Column('company_id', sa.Text(), nullable=True),
        sa.Column('member_id', sa.Text(), nullable=True),
        sa.Column('membership_id', sa.Text(), nullable=True),
        sa.Column('interval_length', sa.Text(), nullable=True),
        sa.Column('start_date', sa.Text(), nullable=True),
        sa.Column('end_date', sa.Text(), nullable=True),
        sa.Column('valid_for', sa.Text(), nullable=True),
        sa.Column('count', sa.Integer(), nullable=False),
        sa.Column('extra', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('synced_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('_id')
    )

    op.create_table(
        'coins_stats',
        sa.Column('_id', sa.Text(), nullable=False),
        sa.Column('extra', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('synced_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('_id')
    )

    op.create_table(
        'fees',
        sa.Column('_id', sa.Text(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('price', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('status', sa.Text(), nullable=False),
        sa.Column('company_id', sa.Text(), nullable=True),
        sa.Column('member_id', sa.Text(), nullable=True),
        sa.Column('location_id', sa.Text(), nullable=True),
        sa.Column('plan_type', sa.Text(), nullable=True),
        sa.Column('issue_date', sa.Text(), nullable=True),
        sa.Column('is_refundable', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_personal', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('modified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('extra', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('synced_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('_id')
    )
    op.create_index('ix_fees_company_id', 'fees', ['company_id'])
    op.create_index('ix_fees_member_id', 'fees', ['member_id'])
    op.create_index('ix_fees_status', 'fees', ['status'])

    op.create_table(
        'revenue_accounts',
        sa.Column('_id', sa.Text(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('default_for', sa.Text(), nullable=True),
        sa.Column('extra', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('synced_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('_id')
    )

    op.create_table(
        'tax_rates',
        sa.Column('_id', sa.Text(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('rate', sa.Integer(), nullable=False),
        sa.Column('extra', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('synced_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('_id')
    )

    op.create_table(
        'memberships',
        sa.Column('_id', sa.Text(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('is_personal', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('status', sa.Text(), nullable=False),
        sa.Column('calculated_status', sa.Text(), nullable=False),
        sa.Column('type', sa.Text(), nullable=False),
        sa.Column('location_id', sa.Text(), nullable=True),
        sa.Column('plan_id', sa.Text(), nullable=True),
        sa.Column('company_id', sa.Text(), nullable=False),
        sa.Column('member_id', sa.Text(), nullable=True),
        sa.Column('start_date', sa.Text(), nullable=True),
        sa.Column('end_date', sa.Text(), nullable=True),
        sa.Column('interval_length', sa.Text(), nullable=True),
        sa.Column('interval_count', sa.Integer(), nullable=False),
        sa.Column('is_locked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('price', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('modified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('extra', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('synced_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('_id')
    )
    op.create_index('ix_memberships_company_id', 'memberships', ['company_id'])
    op.create_index('ix_memberships_member_id', 'memberships', ['member_id'])
    op.create_index('ix_memberships_plan_id', 'memberships', ['plan_id'])
    op.create_index('ix_memberships_status', 'memberships', ['status'])

    op.create_table(
        'plans',
        sa.Column('_id', sa.Text(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.Text(), nullable=False),
        sa.Column('price', sa.Integer(), nullable=False),
        sa.Column('deposit', sa.Integer(), nullable=False),
        sa.Column('interval_length', sa.Text(), nullable=False),
        sa.Column('interval_count', sa.Integer(), nullable=False),
        sa.Column('should_prorate', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('use_coins', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('for_members', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('for_team_members', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('for_non_members', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('extra', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('synced_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('_id')
    )

    op.create_table(
        'resource_rates',
        sa.Column('_id', sa.Text(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('type', sa.Text(), nullable=False),
        sa.Column('interval_length', sa.Text(), nullable=False),
        sa.Column('interval_count', sa.Integer(), nullable=False),
        sa.Column('price', sa.Integer(), nullable=False),
        sa.Column('should_prorate', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('use_coins', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('revenue_account_id', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('extra', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('synced_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('_id')
    )

    op.create_table(
        'contracts',
        sa.Column('_id', sa.Text(), nullable=False),
        sa.Column('extra', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('synced_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('_id')
    )

    # Create Visits & Check-ins tables
    op.create_table(
        'visits',
        sa.Column('_id', sa.Text(), nullable=False),
        sa.Column('member_id', sa.Text(), nullable=False),
        sa.Column('visitor_id', sa.Text(), nullable=False),
        sa.Column('location_id', sa.Text(), nullable=True),
        sa.Column('start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('extra', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('synced_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('_id')
    )

    op.create_table(
        'checkins',
        sa.Column('_id', sa.Text(), nullable=False),
        sa.Column('start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('location_id', sa.Text(), nullable=True),
        sa.Column('company_id', sa.Text(), nullable=True),
        sa.Column('member_id', sa.Text(), nullable=True),
        sa.Column('extra', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('synced_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('_id')
    )

    # Create Webhooks table
    op.create_table(
        'webhooks',
        sa.Column('_id', sa.Text(), nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('secret', sa.Text(), nullable=True),
        sa.Column('extra', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('synced_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('_id')
    )

    # Create SyncJob table
    op.create_table(
        'sync_jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('endpoint', sa.Text(), nullable=False),
        sa.Column('status', sa.Text(), nullable=False),
        sa.Column('last_cursor', sa.Text(), nullable=True),
        sa.Column('records_fetched', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('records_upserted', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_sync_jobs_endpoint_status', 'sync_jobs', ['endpoint', 'status'])


def downgrade() -> None:
    # Drop tables in reverse order of creation
    op.drop_index('ix_sync_jobs_endpoint_status', 'sync_jobs')
    op.drop_table('sync_jobs')
    
    op.drop_table('webhooks')
    op.drop_table('checkins')
    op.drop_table('visits')
    
    op.drop_table('contracts')
    op.drop_index('ix_memberships_status', 'memberships')
    op.drop_index('ix_memberships_plan_id', 'memberships')
    op.drop_index('ix_memberships_member_id', 'memberships')
    op.drop_index('ix_memberships_company_id', 'memberships')
    op.drop_table('memberships')
    
    op.drop_table('resource_rates')
    op.drop_table('plans')
    
    op.drop_table('tax_rates')
    op.drop_table('revenue_accounts')
    
    op.drop_index('ix_fees_status', 'fees')
    op.drop_index('ix_fees_member_id', 'fees')
    op.drop_index('ix_fees_company_id', 'fees')
    op.drop_table('fees')
    
    op.drop_table('coins_stats')
    op.drop_table('credits')
    
    op.drop_index('ix_charges_payment_id', 'charges')
    op.drop_table('charges')
    
    op.drop_index('ix_payments_date', 'payments')
    op.drop_index('ix_payments_status', 'payments')
    op.drop_table('payments')
    
    op.drop_table('ticket_options')
    op.drop_index('ix_tickets_status', 'tickets')
    op.drop_index('ix_tickets_company_id', 'tickets')
    op.drop_table('tickets')
    
    op.drop_table('events')
    op.drop_table('posts')
    
    op.drop_table('floors')
    op.drop_table('locations')
    op.drop_table('assignments')
    
    op.drop_index('ix_booking_occurrences_start_end', 'booking_occurrences')
    op.drop_index('ix_booking_occurrences_resource_id', 'booking_occurrences')
    op.drop_index('ix_booking_occurrences_booking_id', 'booking_occurrences')
    op.drop_table('booking_occurrences')
    
    op.drop_index('ix_bookings_start_end', 'bookings')
    op.drop_index('ix_bookings_company_id', 'bookings')
    op.drop_index('ix_bookings_resource_id', 'bookings')
    op.drop_table('bookings')
    
    op.drop_table('resource_types')
    
    op.drop_index('ix_resources_floor_id', 'resources')
    op.drop_index('ix_resources_type', 'resources')
    op.drop_index('ix_resources_location_id', 'resources')
    op.drop_table('resources')
    
    op.drop_table('opportunities')
    op.drop_table('visitors')
    
    op.drop_index('ix_companies_status', 'companies')
    op.drop_index('ix_companies_location_id', 'companies')
    op.drop_table('companies')
    
    op.drop_index('ix_members_status', 'members')
    op.drop_index('ix_members_location_id', 'members')
    op.drop_index('ix_members_company_id', 'members')
    op.drop_table('members')
