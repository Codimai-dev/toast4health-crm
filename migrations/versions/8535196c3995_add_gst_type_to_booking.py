"""add_gst_type_to_booking

Revision ID: 8535196c3995
Revises: abc123def456
Create Date: 2025-12-26 12:14:53.584246

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8535196c3995'
down_revision = 'abc123def456'
branch_labels = None
depends_on = None


def upgrade():
    # Add gst_type column to booking table with default value 'exclusive'
    # Check if column already exists before adding (for safety)
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('booking')]
    
    if 'gst_type' not in columns:
        op.add_column('booking', sa.Column('gst_type', sa.String(length=20), nullable=False, server_default='exclusive'))


def downgrade():
    # Remove gst_type column from booking table
    op.drop_column('booking', 'gst_type')
