"""initial_migration_create_all_tables

Revision ID: 001
Revises:
Create Date: 2025-12-30 18:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create processor_events table
    op.create_table(
        'processor_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('event_id', sa.String(length=255), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('restaurant_id', sa.String(length=255), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('fee', sa.Integer(), nullable=False),
        sa.Column('event_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('event_id')
    )
    op.create_index(op.f('ix_processor_events_event_id'), 'processor_events', ['event_id'], unique=True)
    op.create_index(op.f('ix_processor_events_id'), 'processor_events', ['id'], unique=False)
    op.create_index(op.f('ix_processor_events_restaurant_id'), 'processor_events', ['restaurant_id'], unique=False)
    op.create_index('idx_processor_events_restaurant_occurred', 'processor_events', ['restaurant_id', 'occurred_at'], unique=False)

    # Create ledger_entries table
    op.create_table(
        'ledger_entries',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('restaurant_id', sa.String(length=255), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('entry_type', sa.Enum('CHARGE', 'FEE', 'REFUND', 'REFUND_FEE', 'PAYOUT_RESERVE', 'PAYOUT_RELEASE', name='ledgerentrytype'), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('reference_type', sa.String(length=100), nullable=False),
        sa.Column('reference_id', sa.String(length=255), nullable=False),
        sa.Column('entry_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ledger_entries_id'), 'ledger_entries', ['id'], unique=False)
    op.create_index(op.f('ix_ledger_entries_restaurant_id'), 'ledger_entries', ['restaurant_id'], unique=False)
    op.create_index('idx_ledger_restaurant_currency', 'ledger_entries', ['restaurant_id', 'currency'], unique=False)
    op.create_index('idx_ledger_reference', 'ledger_entries', ['reference_type', 'reference_id'], unique=False)

    # Create payouts table
    op.create_table(
        'payouts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('payout_id', sa.String(length=255), nullable=False),
        sa.Column('restaurant_id', sa.String(length=255), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('CREATED', 'PAID', 'FAILED', name='payoutstatus'), nullable=False),
        sa.Column('as_of_date', sa.Date(), nullable=False),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('payout_id'),
        sa.UniqueConstraint('restaurant_id', 'currency', 'as_of_date', name='uq_payout_restaurant_currency_date')
    )
    op.create_index(op.f('ix_payouts_id'), 'payouts', ['id'], unique=False)
    op.create_index(op.f('ix_payouts_payout_id'), 'payouts', ['payout_id'], unique=True)
    op.create_index(op.f('ix_payouts_restaurant_id'), 'payouts', ['restaurant_id'], unique=False)
    op.create_index(op.f('ix_payouts_status'), 'payouts', ['status'], unique=False)
    op.create_index('idx_payouts_restaurant', 'payouts', ['restaurant_id', 'currency', 'as_of_date'], unique=False)

    # Create payout_items table
    op.create_table(
        'payout_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('payout_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('item_type', sa.String(length=100), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['payout_id'], ['payouts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payout_items_id'), 'payout_items', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_payout_items_id'), table_name='payout_items')
    op.drop_table('payout_items')
    op.drop_index('idx_payouts_restaurant', table_name='payouts')
    op.drop_index(op.f('ix_payouts_status'), table_name='payouts')
    op.drop_index(op.f('ix_payouts_restaurant_id'), table_name='payouts')
    op.drop_index(op.f('ix_payouts_payout_id'), table_name='payouts')
    op.drop_index(op.f('ix_payouts_id'), table_name='payouts')
    op.drop_table('payouts')
    op.drop_index('idx_ledger_reference', table_name='ledger_entries')
    op.drop_index('idx_ledger_restaurant_currency', table_name='ledger_entries')
    op.drop_index(op.f('ix_ledger_entries_restaurant_id'), table_name='ledger_entries')
    op.drop_index(op.f('ix_ledger_entries_id'), table_name='ledger_entries')
    op.drop_table('ledger_entries')
    op.drop_index('idx_processor_events_restaurant_occurred', table_name='processor_events')
    op.drop_index(op.f('ix_processor_events_restaurant_id'), table_name='processor_events')
    op.drop_index(op.f('ix_processor_events_id'), table_name='processor_events')
    op.drop_index(op.f('ix_processor_events_event_id'), table_name='processor_events')
    op.drop_table('processor_events')
