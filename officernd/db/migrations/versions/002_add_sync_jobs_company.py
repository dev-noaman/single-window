"""Add sync_jobs_company table for tracking per-company sync operations

Revision ID: 002_add_sync_jobs_company
Revises: 001_initial_schema
Create Date: 2026-02-08 19:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_add_sync_jobs_company'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create sync_jobs_company table
    op.create_table(
        'sync_jobs_company',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('company_id', sa.Text(), nullable=False),
        sa.Column('company_name', sa.Text(), nullable=False),
        sa.Column('status', sa.Text(), nullable=False),
        sa.Column('endpoints_completed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('endpoints_failed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('endpoints_skipped', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_records_fetched', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_records_upserted', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    # Create indexes for efficient queries
    op.create_index('ix_sync_jobs_company_id_status', 'sync_jobs_company', ['company_id', 'status'])
    op.create_index('ix_sync_jobs_company_status', 'sync_jobs_company', ['status'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_sync_jobs_company_status', table_name='sync_jobs_company')
    op.drop_index('ix_sync_jobs_company_id_status', table_name='sync_jobs_company')

    # Drop table
    op.drop_table('sync_jobs_company')
