"""Add unified dropdown groups for all modules

Revision ID: add_unified_dropdown_groups
Revises: 
Create Date: 2026-01-02 18:47:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = 'add_unified_dropdown_groups'
down_revision = '97a834849ada'  # add_tds_fields_to_payments
branch_labels = None
depends_on = None


def upgrade():
    """Add initial dropdown values for new groups."""
    # Get connection
    conn = op.get_bind()
    
    # Define default dropdown values for new groups
    new_dropdowns = [
        # B2B Lead Types
        ('B2BLeadType', 'corporate', 'Corporate', 1, True),
        ('B2BLeadType', 'sme', 'SME', 2, True),
        ('B2BLeadType', 'startup', 'Startup', 3, True),
        ('B2BLeadType', 'enterprise', 'Enterprise', 4, True),
        
        # B2B Meeting Status
        ('B2BMeetingStatus', 'scheduled', 'Scheduled', 1, True),
        ('B2BMeetingStatus', 'completed', 'Completed', 2, True),
        ('B2BMeetingStatus', 'cancelled', 'Cancelled', 3, True),
        ('B2BMeetingStatus', 'rescheduled', 'Rescheduled', 4, True),
        
        # Follow-up Outcomes (migrate from enum)
        ('FollowUpOutcome', 'CALLED', 'Called', 1, True),
        ('FollowUpOutcome', 'WHATSAPP', 'WhatsApp', 2, True),
        ('FollowUpOutcome', 'EMAIL', 'Email', 3, True),
        ('FollowUpOutcome', 'MEETING', 'Meeting', 4, True),
        ('FollowUpOutcome', 'SCHEDULED', 'Scheduled', 5, True),
        ('FollowUpOutcome', 'NO_RESPONSE', 'No Response', 6, True),
        ('FollowUpOutcome', 'OTHER', 'Other', 7, True),
        
        # Employee Designation
        ('EmployeeDesignation', 'manager', 'Manager', 1, True),
        ('EmployeeDesignation', 'supervisor', 'Supervisor', 2, True),
        ('EmployeeDesignation', 'executive', 'Executive', 3, True),
        ('EmployeeDesignation', 'assistant', 'Assistant', 4, True),
        ('EmployeeDesignation', 'intern', 'Intern', 5, True),
        
        # Gender
        ('Gender', 'MALE', 'Male', 1, True),
        ('Gender', 'FEMALE', 'Female', 2, True),
        ('Gender', 'OTHER', 'Other', 3, True),
        
        # GST Type
        ('GSTType', 'exclusive', 'Exclusive', 1, True),
        ('GSTType', 'inclusive', 'Inclusive', 2, True),
        
        # Payment Status
        ('PaymentStatus', 'Pending', 'Pending', 1, True),
        ('PaymentStatus', 'Received', 'Received', 2, True),
        ('PaymentStatus', 'Partial', 'Partial', 3, True),
        ('PaymentStatus', 'Paid', 'Paid', 4, True),
        
        # Payment Method
        ('PaymentMethod', 'Cash', 'Cash', 1, True),
        ('PaymentMethod', 'Bank Transfer', 'Bank Transfer', 2, True),
        ('PaymentMethod', 'Cheque', 'Cheque', 3, True),
        ('PaymentMethod', 'UPI', 'UPI', 4, True),
        ('PaymentMethod', 'Card', 'Card', 5, True),
        ('PaymentMethod', 'Other', 'Other', 6, True),
        
        # TDS Section
        ('TDSSection', '194C', '194C - Payments to contractors', 1, True),
        ('TDSSection', '194J', '194J - Professional or technical services', 2, True),
        ('TDSSection', '194H', '194H - Commission or brokerage', 3, True),
        ('TDSSection', '194I', '194I - Rent', 4, True),
        ('TDSSection', '194A', '194A - Interest other than on securities', 5, True),
        
        # Payment Category
        ('PaymentCategory', 'Purchases', 'Purchases', 1, True),
        ('PaymentCategory', 'Office Rent', 'Office Rent', 2, True),
        ('PaymentCategory', 'Utilities', 'Utilities', 3, True),
        ('PaymentCategory', 'Salary', 'Salary', 4, True),
        ('PaymentCategory', 'Marketing', 'Marketing', 5, True),
        ('PaymentCategory', 'Miscellaneous', 'Miscellaneous', 6, True),
    ]
    
    # Insert new dropdown values
    for group, key, value, sort_order, is_active in new_dropdowns:
        # Check if this entry already exists
        result = conn.execute(
            sa.text("SELECT COUNT(*) FROM setting WHERE `group` = :group AND `key` = :key"),
            {"group": group, "key": key}
        ).scalar()
        
        if result == 0:
            conn.execute(
                sa.text("""
                    INSERT INTO setting (`group`, `key`, value, sort_order, is_active, created_at, updated_at)
                    VALUES (:group, :key, :value, :sort_order, :is_active, :created_at, :updated_at)
                """),
                {
                    "group": group,
                    "key": key,
                    "value": value,
                    "sort_order": sort_order,
                    "is_active": is_active,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            )


def downgrade():
    """Remove the unified dropdown groups."""
    conn = op.get_bind()
    
    # Remove all new groups
    groups_to_remove = [
        'B2BLeadType', 'B2BMeetingStatus', 'FollowUpOutcome',
        'EmployeeDesignation', 'Gender', 'GSTType', 'PaymentStatus',
        'PaymentMethod', 'TDSSection', 'PaymentCategory'
    ]
    
    for group in groups_to_remove:
        conn.execute(
            sa.text("DELETE FROM setting WHERE `group` = :group"),
            {"group": group}
        )
