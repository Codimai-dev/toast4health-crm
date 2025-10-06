"""SQLAlchemy models for the CRM application."""

import enum
import json
from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index, CheckConstraint, func, text
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates, declared_attr
from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class UserRole(enum.Enum):
    """User roles enumeration."""
    ADMIN = "ADMIN"
    SALES = "SALES"
    OPS = "OPS"
    FINANCE = "FINANCE"
    VIEWER = "VIEWER"


class LeadStatus(enum.Enum):
    """Lead status enumeration."""
    NEW = "NEW"
    FOLLOW_UP = "FOLLOW_UP"
    PROSPECT = "PROSPECT"
    CONVERTED = "CONVERTED"
    LOST = "LOST"


class LeadType(enum.Enum):
    """Lead type enumeration."""
    B2C = "B2C"
    B2B = "B2B"


class FollowUpOutcome(enum.Enum):
    """Follow-up outcome enumeration."""
    CALLED = "CALLED"
    WHATSAPP = "WHATSAPP"
    EMAIL = "EMAIL"
    MEETING = "MEETING"
    SCHEDULED = "SCHEDULED"
    NO_RESPONSE = "NO_RESPONSE"
    OTHER = "OTHER"


class Gender(enum.Enum):
    """Gender enumeration."""
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"


class AttendanceStatus(enum.Enum):
    """Attendance status enumeration."""
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    HALF_DAY = "HALF_DAY"
    LATE = "LATE"


class LeaveType(enum.Enum):
    """Leave type enumeration."""
    CASUAL = "CASUAL"
    SICK = "SICK"
    EARNED = "EARNED"
    MATERNITY = "MATERNITY"
    PATERNITY = "PATERNITY"
    OTHER = "OTHER"


class LeaveStatus(enum.Enum):
    """Leave status enumeration."""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class TaskStatus(enum.Enum):
    """Task status enumeration."""
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class TaskPriority(enum.Enum):
    """Task priority enumeration."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class LeadSource(enum.Enum):
    """Lead source enumeration."""
    REFERRAL = "REFERRAL"
    WEBSITE = "WEBSITE"
    SOCIAL_MEDIA = "SOCIAL_MEDIA"
    ADVERTISEMENT = "ADVERTISEMENT"
    COLD_CALL = "COLD_CALL"
    WALK_IN = "WALK_IN"
    OTHER = "OTHER"


class AuditAction(enum.Enum):
    """Audit action enumeration."""
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserTrackingMixin:
    """Mixin for created_by and updated_by user tracking."""
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Relationships for tracking users
    @declared_attr
    def creator(cls):
        return db.relationship('User', foreign_keys=[cls.created_by], post_update=True)
    
    @declared_attr
    def updater(cls):
        return db.relationship('User', foreign_keys=[cls.updated_by], post_update=True)


class User(UserMixin, db.Model, TimestampMixin, UserTrackingMixin):
    """User model for authentication and authorization."""

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.VIEWER)
    permissions = db.Column(db.Text, nullable=True)  # JSON string of allowed modules
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    last_login_at = db.Column(db.DateTime, nullable=True)
    
    def set_password(self, password: str) -> None:
        """Hash and set the password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)
    
    @property
    def allowed_modules(self):
        """Get list of allowed modules for this user."""
        if self.role == UserRole.ADMIN:
            # Admins have access to everything
            return ['dashboard', 'leads_b2c', 'leads_b2b', 'follow_ups', 'customers',
                   'bookings', 'employees', 'expenses', 'channel_partners', 'services', 'settings']

        if self.permissions:
            try:
                return json.loads(self.permissions)
            except (json.JSONDecodeError, TypeError):
                pass

        # Default permissions based on role
        defaults = {
            UserRole.SALES: ['dashboard', 'leads_b2c', 'leads_b2b', 'follow_ups'],
            UserRole.OPS: ['dashboard', 'customers', 'bookings', 'employees', 'expenses', 'channel_partners', 'services'],
            UserRole.FINANCE: ['dashboard', 'bookings', 'expenses'],
            UserRole.VIEWER: ['dashboard']  # Read-only access
        }
        return defaults.get(self.role, ['dashboard'])

    @allowed_modules.setter
    def allowed_modules(self, modules):
        """Set allowed modules for this user."""
        if isinstance(modules, list):
            self.permissions = json.dumps(modules)
        else:
            self.permissions = None

    def has_module_access(self, module_name: str) -> bool:
        """Check if user has access to a specific module."""
        if self.role == UserRole.ADMIN:
            return True
        return module_name in self.allowed_modules

    def has_permission(self, required_role: UserRole) -> bool:
        """Check if user has required permission level."""
        role_hierarchy = {
            UserRole.VIEWER: 1,
            UserRole.FINANCE: 2,
            UserRole.OPS: 3,
            UserRole.SALES: 4,
            UserRole.ADMIN: 5
        }
        return role_hierarchy.get(self.role, 0) >= role_hierarchy.get(required_role, 0)
    
    def __repr__(self):
        return f'<User {self.email}>'


class B2CLead(db.Model, TimestampMixin, UserTrackingMixin):
    """B2C Lead model."""

    __tablename__ = 'b2c_lead'

    enquiry_id = db.Column(db.String(20), primary_key=True, nullable=False, unique=True, index=True)
    customer_name = db.Column(db.String(100), nullable=False)
    contact_no = db.Column(db.String(20), nullable=False, index=True)
    email = db.Column(db.String(120), nullable=True, index=True)
    enquiry_date = db.Column(db.Date, nullable=False, index=True)
    source = db.Column(db.String(50), nullable=True)
    services = db.Column(db.String(200), nullable=True)
    referred_by = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='NEW', index=True)
    comment = db.Column(db.Text, nullable=True)
    
    # Follow-up fields
    followup1 = db.Column(db.Date, nullable=True)
    followup1_detail = db.Column(db.Text, nullable=True)
    followup2 = db.Column(db.Date, nullable=True)
    followup2_detail = db.Column(db.Text, nullable=True)
    followup3 = db.Column(db.Date, nullable=True)
    followup3_detail = db.Column(db.Text, nullable=True)
    
    # Customer reference (business logic, not FK)
    customer_id = db.Column(db.String(20), nullable=True)
    
    # Relationships
    follow_ups = db.relationship('FollowUp', backref='b2c_lead_ref', lazy='dynamic', 
                                foreign_keys='FollowUp.b2c_lead_id')
    
    @validates('email')
    def validate_email(self, key, email):
        if email and '@' not in email:
            raise ValueError('Invalid email address')
        return email
    
    def __repr__(self):
        return f'<B2CLead {self.enquiry_id}: {self.customer_name}>'

    @staticmethod
    def generate_enquiry_id():
        """Generate a unique enquiry ID in format B2C-XXX."""
        # Find the highest existing enquiry ID
        existing_ids = db.session.query(B2CLead.enquiry_id).filter(
            B2CLead.enquiry_id.like('B2C-%')
        ).all()

        if existing_ids:
            # Extract the sequential numbers and find the max
            numbers = []
            for eid in existing_ids:
                try:
                    num_part = eid[0].split('-')[-1]
                    numbers.append(int(num_part))
                except (IndexError, ValueError):
                    continue

            next_num = max(numbers) + 1 if numbers else 1
        else:
            next_num = 1

        return f'B2C-{next_num:03d}'


# Indexes for B2CLead
Index('idx_b2c_lead_enquiry_email_contact_status', 
      B2CLead.enquiry_id, B2CLead.email, B2CLead.contact_no, B2CLead.status)


class B2BLead(db.Model, TimestampMixin, UserTrackingMixin):
    """B2B Lead model."""
    
    __tablename__ = 'b2b_lead'
    
    id = db.Column(db.Integer, primary_key=True)
    sr_no = db.Column(db.String(20), nullable=True, unique=True)
    t4h_spoc = db.Column(db.String(100), nullable=True)
    date = db.Column(db.Date, nullable=True, index=True)
    organization_name = db.Column(db.String(200), nullable=False, index=True)
    organization_email = db.Column(db.String(120), nullable=True, index=True)
    location = db.Column(db.String(100), nullable=True)
    type_of_leads = db.Column(db.String(100), nullable=True)
    org_poc_name_and_role = db.Column(db.String(200), nullable=True)
    employee_size = db.Column(db.String(50), nullable=True)
    employee_wellness_program = db.Column(db.String(100), nullable=True)
    budget_of_wellness_program = db.Column(db.String(100), nullable=True)
    last_wellness_activity_done = db.Column(db.String(200), nullable=True)
    
    
    # Relationships
    follow_ups = db.relationship('FollowUp', backref='b2b_lead_ref', lazy='dynamic',
                                foreign_keys='FollowUp.b2b_lead_id')
    
    # Relationships
    follow_ups = db.relationship('FollowUp', backref='b2b_lead_ref', lazy='dynamic',
                                foreign_keys='FollowUp.b2b_lead_id')
    
    def __repr__(self):
        return f'<B2BLead {self.organization_name}>'

    @staticmethod
    def generate_sr_no():
        """Generate a unique sr_no in format B2B-XXX."""
        # Find the highest existing sr_no
        existing_sr_nos = db.session.query(B2BLead.sr_no).filter(
            B2BLead.sr_no.like('B2B-%')
        ).all()

        if existing_sr_nos:
            # Extract the sequential numbers and find the max
            numbers = []
            for sr_no in existing_sr_nos:
                try:
                    num_part = sr_no[0].split('-')[-1]
                    numbers.append(int(num_part))
                except (IndexError, ValueError):
                    continue

            next_num = max(numbers) + 1 if numbers else 1
        else:
            next_num = 1

        return f'B2B-{next_num:03d}'


# Indexes for B2BLead
Index('idx_b2b_lead_org_email',
      B2BLead.organization_name, B2BLead.organization_email)


class FollowUp(db.Model, TimestampMixin):
    """Follow-up model for both B2C and B2B leads."""

    __tablename__ = 'follow_up'

    id = db.Column(db.Integer, primary_key=True)
    lead_type = db.Column(db.Enum(LeadType), nullable=False)
    b2c_lead_id = db.Column(db.String(20), db.ForeignKey('b2c_lead.enquiry_id'), nullable=True)
    b2b_lead_id = db.Column(db.Integer, db.ForeignKey('b2b_lead.id'), nullable=True)
    follow_up_on = db.Column(db.Date, nullable=False, index=True)
    notes = db.Column(db.Text, nullable=True)
    outcome = db.Column(db.Enum(FollowUpOutcome), nullable=False)
    next_follow_up_on = db.Column(db.Date, nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    owner = db.relationship('User', backref='follow_ups')
    
    # Constraint: exactly one of b2c_lead_id or b2b_lead_id must be non-null
    __table_args__ = (
        CheckConstraint(
            '(b2c_lead_id IS NOT NULL AND b2b_lead_id IS NULL) OR '
            '(b2c_lead_id IS NULL AND b2b_lead_id IS NOT NULL)',
            name='check_exactly_one_lead'
        ),
    )
    
    def __repr__(self):
        lead_ref = f"B2C-{self.b2c_lead_id}" if self.b2c_lead_id else f"B2B-{self.b2b_lead_id}"
        return f'<FollowUp {lead_ref}: {self.follow_up_on}>'


class Meeting(db.Model, TimestampMixin, UserTrackingMixin):
    """Meeting model for B2B leads."""

    __tablename__ = 'meeting'

    id = db.Column(db.Integer, primary_key=True)
    b2b_lead_id = db.Column(db.Integer, db.ForeignKey('b2b_lead.id'), nullable=False)
    meeting1_date = db.Column(db.Date, nullable=True)
    meeting2_date = db.Column(db.Date, nullable=True)
    meeting1_notes = db.Column(db.Text, nullable=True)
    meeting1_task_done = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    task_done = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), nullable=True)

    # Relationships
    b2b_lead = db.relationship('B2BLead', backref='meetings')

    def __repr__(self):
        return f'<Meeting {self.b2b_lead_id}: {self.meeting1_date}>'


class Customer(db.Model, TimestampMixin, UserTrackingMixin):
    """Customer model."""
    
    __tablename__ = 'customer'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_code = db.Column(db.String(20), nullable=False, unique=True, index=True)
    services = db.Column(db.String(200), nullable=True)
    customer_name = db.Column(db.String(100), nullable=False, index=True)
    contact_no = db.Column(db.String(20), nullable=False, index=True)
    email = db.Column(db.String(120), nullable=True, index=True)
    channel_partner_id = db.Column(db.Integer, db.ForeignKey('channel_partner.id'), nullable=True)
    
    # Relationships
    channel_partner = db.relationship('ChannelPartner', backref='customers')
    
    def __repr__(self):
        return f'<Customer {self.customer_code}: {self.customer_name}>'


# Indexes for Customer
Index('idx_customer_name_contact_email', Customer.customer_name, Customer.contact_no, Customer.email)


class Booking(db.Model, TimestampMixin, UserTrackingMixin):
    """Booking model with financial calculations."""

    __tablename__ = 'booking'

    id = db.Column(db.Integer, primary_key=True)
    booking_code = db.Column(db.String(20), nullable=False, unique=True, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=True)
    customer_mob = db.Column(db.String(20), nullable=False)
    customer_name = db.Column(db.String(100), nullable=False, index=True)
    services = db.Column(db.String(200), nullable=False)
    charge_type = db.Column(db.String(20), nullable=False, default='Fixed charge')
    start_date = db.Column(db.Date, nullable=True, index=True)
    end_date = db.Column(db.Date, nullable=True)
    shift_hours = db.Column(db.Integer, nullable=True)
    service_charge = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    other_expanse = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    gst_percentage = db.Column(db.Integer, nullable=False, default=0)
    gst_value = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    amount_paid = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    pending_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    last_payment_date = db.Column(db.Date, nullable=True)
    employee_assigned_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=True)
    
    # Relationships
    customer = db.relationship('Customer', backref='bookings')
    employee_assigned = db.relationship('Employee', backref='bookings')
    expenses = db.relationship('Expense', backref='booking', lazy='dynamic')
    
    @hybrid_property
    def computed_gst_value(self):
        """Compute GST value based on service charge and GST percentage."""
        base_amount = (self.service_charge or 0) + (self.other_expanse or 0)
        return base_amount * (self.gst_percentage or 0) / 100
    
    @hybrid_property
    def computed_pending_amount(self):
        """Compute pending amount."""
        return (self.total_amount or 0) - (self.amount_paid or 0)
    
    def calculate_totals(self):
        """Calculate GST value and pending amount."""
        base_service_charge = self.service_charge or 0

        if self.charge_type == 'Recurring charge' and self.start_date and self.end_date and self.shift_hours:
            days = (self.end_date - self.start_date).days + 1
            shifts_per_day = 24 / self.shift_hours
            total_shifts = Decimal(days * shifts_per_day)
            base_service_charge *= total_shifts

        base_amount = base_service_charge + (self.other_expanse or 0)
        self.gst_value = base_amount * (self.gst_percentage or 0) / 100
        self.total_amount = base_amount + self.gst_value
        self.pending_amount = self.total_amount - (self.amount_paid or 0)
    
    def __repr__(self):
        return f'<Booking {self.booking_code}: {self.customer_name}>'

    @staticmethod
    def generate_booking_code():
        """Generate a unique booking code in format BOOK-XXX."""
        # Find the highest existing booking code
        existing_codes = db.session.query(Booking.booking_code).filter(
            Booking.booking_code.like('BOOK-%')
        ).all()

        if existing_codes:
            # Extract the sequential numbers and find the max
            numbers = []
            for code in existing_codes:
                try:
                    num_part = code[0].split('-')[-1]
                    numbers.append(int(num_part))
                except (IndexError, ValueError):
                    continue

            next_num = max(numbers) + 1 if numbers else 1
        else:
            next_num = 1

        return f'BOOK-{next_num:03d}'


# Indexes for Booking
Index('idx_booking_code_customer_date', Booking.booking_code, Booking.customer_name, Booking.start_date)
Index('idx_booking_customer_id', Booking.customer_id)


class Employee(db.Model, TimestampMixin, UserTrackingMixin):
    """Employee model."""
    
    __tablename__ = 'employee'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_code = db.Column(db.String(20), nullable=False, unique=True, index=True)
    employ_type = db.Column(db.String(50), nullable=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    contact_no = db.Column(db.String(20), nullable=False, index=True)
    dob = db.Column(db.Date, nullable=True)
    degree = db.Column(db.String(100), nullable=True)
    temporary_address = db.Column(db.Text, nullable=True)
    permanent_address = db.Column(db.Text, nullable=True)
    employ_image = db.Column(db.String(200), nullable=True)
    aadhar_no = db.Column(db.String(20), nullable=True)
    total_experience = db.Column(db.String(50), nullable=True)
    skill_set = db.Column(db.Text, nullable=True)
    gender = db.Column(db.Enum(Gender), nullable=True)
    designation = db.Column(db.String(100), nullable=True, index=True)
    whatsapp_no = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True, index=True)
    pdf_link = db.Column(db.String(200), nullable=True)
    bank_name = db.Column(db.String(100), nullable=True)
    branch_name = db.Column(db.String(100), nullable=True)
    account_no = db.Column(db.String(50), nullable=True)
    ifsc_code = db.Column(db.String(20), nullable=True)
    
    def __repr__(self):
        return f'<Employee {self.employee_code}: {self.name}>'


# Indexes for Employee
Index('idx_employee_name_email_contact_designation',
      Employee.name, Employee.email, Employee.contact_no, Employee.designation)


class Attendance(db.Model, TimestampMixin, UserTrackingMixin):
    """Attendance tracking model."""

    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(db.Enum(AttendanceStatus), nullable=False, default=AttendanceStatus.PRESENT)
    check_in_time = db.Column(db.Time, nullable=True)
    check_out_time = db.Column(db.Time, nullable=True)
    working_hours = db.Column(db.Numeric(4, 2), nullable=True)  # Hours worked
    notes = db.Column(db.Text, nullable=True)

    # Relationships
    employee = db.relationship('Employee', backref='attendance_records')

    __table_args__ = (
        Index('idx_attendance_employee_date', 'employee_id', 'date', unique=True),
    )

    def __repr__(self):
        return f'<Attendance {self.employee.name} on {self.date}: {self.status.value}>'


class Leave(db.Model, TimestampMixin, UserTrackingMixin):
    """Leave management model."""

    __tablename__ = 'leave'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False, index=True)
    leave_type = db.Column(db.Enum(LeaveType), nullable=False)
    start_date = db.Column(db.Date, nullable=False, index=True)
    end_date = db.Column(db.Date, nullable=False, index=True)
    days_requested = db.Column(db.Numeric(4, 1), nullable=False)
    reason = db.Column(db.Text, nullable=True)
    status = db.Column(db.Enum(LeaveStatus), nullable=False, default=LeaveStatus.PENDING)
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    comments = db.Column(db.Text, nullable=True)

    # Relationships
    employee = db.relationship('Employee', backref='leave_requests')
    approver = db.relationship('User', foreign_keys=[approved_by], backref='approved_leaves')

    def __repr__(self):
        return f'<Leave {self.employee.name}: {self.leave_type.value} ({self.start_date} to {self.end_date})>'


class Task(db.Model, TimestampMixin, UserTrackingMixin):
    """Task assignment model."""

    __tablename__ = 'task'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    assigned_to = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False, index=True)
    assigned_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    priority = db.Column(db.Enum(TaskPriority), nullable=False, default=TaskPriority.MEDIUM)
    status = db.Column(db.Enum(TaskStatus), nullable=False, default=TaskStatus.TODO)
    due_date = db.Column(db.Date, nullable=True, index=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    lead_id = db.Column(db.String(20), nullable=True)  # For lead-related tasks
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=True)

    # Relationships
    employee = db.relationship('Employee', backref='assigned_tasks')
    assigner = db.relationship('User', foreign_keys=[assigned_by], backref='assigned_tasks')
    booking = db.relationship('Booking', backref='tasks')
    customer = db.relationship('Customer', backref='tasks')

    def __repr__(self):
        return f'<Task {self.title}: {self.employee.name} ({self.status.value})>'


class PerformanceMetric(db.Model, TimestampMixin):
    """Performance metrics for employees."""

    __tablename__ = 'performance_metric'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False, index=True)
    metric_date = db.Column(db.Date, nullable=False, index=True)
    leads_assigned = db.Column(db.Integer, nullable=False, default=0)
    leads_converted = db.Column(db.Integer, nullable=False, default=0)
    bookings_completed = db.Column(db.Integer, nullable=False, default=0)
    revenue_generated = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    follow_ups_done = db.Column(db.Integer, nullable=False, default=0)
    customer_satisfaction = db.Column(db.Numeric(3, 1), nullable=True)  # Rating out of 5
    tasks_completed = db.Column(db.Integer, nullable=False, default=0)
    attendance_percentage = db.Column(db.Numeric(5, 2), nullable=True)  # Monthly percentage

    # Relationships
    employee = db.relationship('Employee', backref='performance_metrics')

    __table_args__ = (
        Index('idx_performance_employee_date', 'employee_id', 'metric_date', unique=True),
    )

    @property
    def conversion_rate(self):
        """Calculate lead conversion rate."""
        if self.leads_assigned > 0:
            return (self.leads_converted / self.leads_assigned) * 100
        return 0

    def __repr__(self):
        return f'<PerformanceMetric {self.employee.name} on {self.metric_date}>'


class Expense(db.Model, TimestampMixin, UserTrackingMixin):
    """Expense model."""
    
    __tablename__ = 'expense'
    
    id = db.Column(db.Integer, primary_key=True)
    expense_code = db.Column(db.String(20), nullable=False, unique=True, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=True, index=True)
    other_id = db.Column(db.String(50), nullable=True)
    category = db.Column(db.String(100), nullable=False, index=True)
    sub_category = db.Column(db.String(100), nullable=True)
    expense_amount = db.Column(db.Numeric(10, 2), nullable=False)
    
    def __repr__(self):
        return f'<Expense {self.expense_code}: {self.category}>'


# Indexes for Expense
Index('idx_expense_date_category_booking', Expense.date, Expense.category, Expense.booking_id)


class ChannelPartner(db.Model, TimestampMixin, UserTrackingMixin):
    """Channel Partner model."""
    
    __tablename__ = 'channel_partner'
    
    id = db.Column(db.Integer, primary_key=True)
    partner_code = db.Column(db.String(20), nullable=False, unique=True, index=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    contact_no = db.Column(db.String(20), nullable=False, index=True)
    email = db.Column(db.String(120), nullable=True, index=True)
    created_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<ChannelPartner {self.partner_code}: {self.name}>'


# Indexes for ChannelPartner
Index('idx_channel_partner_name_contact_email', 
      ChannelPartner.name, ChannelPartner.contact_no, ChannelPartner.email)


class Setting(db.Model, TimestampMixin, UserTrackingMixin):
    """Settings model for managing key-value configurations."""
    
    __tablename__ = 'setting'
    
    id = db.Column(db.Integer, primary_key=True)
    group = db.Column(db.String(50), nullable=False)
    key = db.Column(db.String(100), nullable=False)
    value = db.Column(db.String(200), nullable=False)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    __table_args__ = (
        Index('idx_setting_group_key', 'group', 'key', unique=True),
    )
    
    @classmethod
    def get_options(cls, group: str):
        """Get all active options for a group."""
        return cls.query.filter_by(group=group, is_active=True)\
                       .order_by(cls.sort_order, cls.value).all()
    
    def __repr__(self):
        return f'<Setting {self.group}.{self.key}: {self.value}>'


class Service(db.Model, TimestampMixin, UserTrackingMixin):
    """Service model."""

    __tablename__ = 'service'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Service {self.id}: {self.name}>'


class AuditLog(db.Model):
    """Audit log model for tracking changes."""
    
    __tablename__ = 'audit_log'
    
    id = db.Column(db.Integer, primary_key=True)
    entity = db.Column(db.String(50), nullable=False)
    entity_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.Enum(AuditAction), nullable=False)
    changed_fields = db.Column(db.Text, nullable=True)  # JSON string
    actor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Relationships
    actor = db.relationship('User', backref='audit_logs')
    
    @property
    def changes(self):
        """Parse changed_fields JSON."""
        if self.changed_fields:
            try:
                return json.loads(self.changed_fields)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    @changes.setter
    def changes(self, value):
        """Set changed_fields as JSON."""
        if value:
            self.changed_fields = json.dumps(value, default=str)
        else:
            self.changed_fields = None
    
    def __repr__(self):
        return f'<AuditLog {self.entity}:{self.entity_id} {self.action}>'