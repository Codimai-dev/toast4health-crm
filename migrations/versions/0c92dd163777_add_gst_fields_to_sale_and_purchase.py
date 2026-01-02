"""add_gst_fields_to_sale_and_purchase

Revision ID: 0c92dd163777
Revises: 22ddb772592c
Create Date: 2026-01-02 17:04:40.698128

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0c92dd163777'
down_revision = '22ddb772592c'
branch_labels = None
depends_on = None


def upgrade():
    # Add GST fields to sale table
    op.add_column('sale', sa.Column('base_amount', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'))
    op.add_column('sale', sa.Column('gst_type', sa.String(length=20), nullable=False, server_default='exclusive'))
    op.add_column('sale', sa.Column('gst_percentage', sa.Integer(), nullable=False, server_default='18'))
    op.add_column('sale', sa.Column('gst_amount', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'))
    
    # Add GST fields to purchase table
    op.add_column('purchase', sa.Column('base_amount', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'))
    op.add_column('purchase', sa.Column('gst_type', sa.String(length=20), nullable=False, server_default='exclusive'))
    op.add_column('purchase', sa.Column('gst_percentage', sa.Integer(), nullable=False, server_default='18'))
    op.add_column('purchase', sa.Column('gst_amount', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'))
    
    # Migrate existing data: copy amount to base_amount for existing records
    op.execute('UPDATE sale SET base_amount = amount WHERE base_amount = 0')
    op.execute('UPDATE purchase SET base_amount = amount WHERE base_amount = 0')


def downgrade():
    # Remove GST fields from purchase table
    op.drop_column('purchase', 'gst_amount')
    op.drop_column('purchase', 'gst_percentage')
    op.drop_column('purchase', 'gst_type')
    op.drop_column('purchase', 'base_amount')
    
    # Remove GST fields from sale table
    op.drop_column('sale', 'gst_amount')
    op.drop_column('sale', 'gst_percentage')
    op.drop_column('sale', 'gst_type')
    op.drop_column('sale', 'base_amount')
