"""add camp_id to camp_default

Revision ID: add_camp_id_to_default
Revises: add_unified_dropdown_groups
Create Date: 2026-01-08 23:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_camp_id_to_default'
down_revision = 'add_unified_dropdown_groups'
branch_labels = None
depends_on = None


def upgrade():
    # Add camp_id column to camp_default table
    op.add_column('camp_default', sa.Column('camp_id', sa.String(length=20), nullable=True))


def downgrade():
    # Remove camp_id column from camp_default table
    op.drop_column('camp_default', 'camp_id')
