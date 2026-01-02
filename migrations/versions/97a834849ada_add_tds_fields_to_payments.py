"""add_tds_fields_to_payments

Revision ID: 97a834849ada
Revises: 0c92dd163777
Create Date: 2026-01-02 17:42:25.833472

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '97a834849ada'
down_revision = '0c92dd163777'
branch_labels = None
depends_on = None


def upgrade():
    # Add TDS fields to payment_received table
    op.add_column('payment_received', sa.Column('tds_applicable', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('payment_received', sa.Column('tds_percentage', sa.Numeric(precision=5, scale=2), nullable=True))
    op.add_column('payment_received', sa.Column('tds_amount', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'))
    op.add_column('payment_received', sa.Column('tds_section', sa.String(length=50), nullable=True))
    op.add_column('payment_received', sa.Column('net_amount', sa.Numeric(precision=12, scale=2), nullable=True))
    
    # Add TDS fields to payment_made table
    op.add_column('payment_made', sa.Column('tds_applicable', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('payment_made', sa.Column('tds_percentage', sa.Numeric(precision=5, scale=2), nullable=True))
    op.add_column('payment_made', sa.Column('tds_amount', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'))
    op.add_column('payment_made', sa.Column('tds_section', sa.String(length=50), nullable=True))
    op.add_column('payment_made', sa.Column('net_amount', sa.Numeric(precision=12, scale=2), nullable=True))


def downgrade():
    # Remove TDS fields from payment_made table
    op.drop_column('payment_made', 'net_amount')
    op.drop_column('payment_made', 'tds_section')
    op.drop_column('payment_made', 'tds_amount')
    op.drop_column('payment_made', 'tds_percentage')
    op.drop_column('payment_made', 'tds_applicable')
    
    # Remove TDS fields from payment_received table
    op.drop_column('payment_received', 'net_amount')
    op.drop_column('payment_received', 'tds_section')
    op.drop_column('payment_received', 'tds_amount')
    op.drop_column('payment_received', 'tds_percentage')
    op.drop_column('payment_received', 'tds_applicable')
