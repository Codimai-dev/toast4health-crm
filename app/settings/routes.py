"""Settings routes."""

from flask import render_template, jsonify, flash, redirect, url_for, request
from flask_login import login_required, current_user
from flask_wtf.csrf import validate_csrf, generate_csrf
from app import db
from app.models import (
    User, UserRole, B2CLead, B2BLead, FollowUp, Customer,
    Employee, Expense, ChannelPartner, Setting, AuditLog, Service
)
from app.settings import bp
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError


class UserForm(FlaskForm):
    """User management form for admin."""

    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)],
                            render_kw={'class': 'form-control', 'placeholder': 'Enter full name'})
    email = StringField('Email', validators=[DataRequired(), Email()],
                        render_kw={'class': 'form-control', 'placeholder': 'Enter email'})
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ], render_kw={'class': 'form-control', 'placeholder': 'Enter password'})
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ], render_kw={'class': 'form-control', 'placeholder': 'Confirm password'})
    role = SelectField('Role', validators=[DataRequired()],
                       choices=[(UserRole.SALES.value, 'Sales'), (UserRole.OPS.value, 'Operations'),
                               (UserRole.FINANCE.value, 'Finance'), (UserRole.VIEWER.value, 'Viewer')],
                       render_kw={'class': 'form-select'})

    # Module permissions checkboxes
    dashboard_access = BooleanField('Dashboard', default=True, render_kw={'class': 'form-check-input'})
    leads_b2c_access = BooleanField('B2C Leads', render_kw={'class': 'form-check-input'})
    leads_b2b_access = BooleanField('B2B Leads', render_kw={'class': 'form-check-input'})
    follow_ups_access = BooleanField('Follow-ups', render_kw={'class': 'form-check-input'})
    customers_access = BooleanField('Customers', render_kw={'class': 'form-check-input'})
    employees_access = BooleanField('Employees', render_kw={'class': 'form-check-input'})
    expenses_access = BooleanField('Expenses', render_kw={'class': 'form-check-input'})
    channel_partners_access = BooleanField('Channel Partners', render_kw={'class': 'form-check-input'})
    services_access = BooleanField('Services', render_kw={'class': 'form-check-input'})
    camps_access = BooleanField('Health Camps', render_kw={'class': 'form-check-input'})
    finance_access = BooleanField('Financial Management', render_kw={'class': 'form-check-input'})

    is_active = BooleanField('Active', default=True, render_kw={'class': 'form-check-input'})
    submit = SubmitField('Create User', render_kw={'class': 'btn btn-primary'})

    def validate_email(self, email):
        """Check if email is already registered."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email is already registered.')


class EditUserForm(FlaskForm):
    """Edit user form for admin."""

    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)],
                            render_kw={'class': 'form-control', 'placeholder': 'Enter full name'})
    email = StringField('Email', validators=[DataRequired(), Email()],
                        render_kw={'class': 'form-control', 'placeholder': 'Enter email'})
    role = SelectField('Role', validators=[DataRequired()],
                       choices=[(UserRole.SALES.value, 'Sales'), (UserRole.OPS.value, 'Operations'),
                               (UserRole.FINANCE.value, 'Finance'), (UserRole.VIEWER.value, 'Viewer')],
                       render_kw={'class': 'form-select'})

    # Module permissions checkboxes
    dashboard_access = BooleanField('Dashboard', default=True, render_kw={'class': 'form-check-input'})
    leads_b2c_access = BooleanField('B2C Leads', render_kw={'class': 'form-check-input'})
    leads_b2b_access = BooleanField('B2B Leads', render_kw={'class': 'form-check-input'})
    follow_ups_access = BooleanField('Follow-ups', render_kw={'class': 'form-check-input'})
    customers_access = BooleanField('Customers', render_kw={'class': 'form-check-input'})
    employees_access = BooleanField('Employees', render_kw={'class': 'form-check-input'})
    expenses_access = BooleanField('Expenses', render_kw={'class': 'form-check-input'})
    channel_partners_access = BooleanField('Channel Partners', render_kw={'class': 'form-check-input'})
    services_access = BooleanField('Services', render_kw={'class': 'form-check-input'})
    camps_access = BooleanField('Health Camps', render_kw={'class': 'form-check-input'})
    finance_access = BooleanField('Financial Management', render_kw={'class': 'form-check-input'})

    is_active = BooleanField('Active', render_kw={'class': 'form-check-input'})
    submit = SubmitField('Update User', render_kw={'class': 'btn btn-primary'})

    def __init__(self, original_email=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_email = original_email

    def validate_email(self, email):
        """Check if email is already registered by another user."""
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('This email is already registered.')


@bp.route('/')
@login_required
def index():
    """Settings page with danger zone."""
    if not current_user.has_permission(UserRole.ADMIN):
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard.index'))

    return render_template('settings/index.html')


@bp.route('/dropdowns')
@login_required
def dropdowns():
    """Unified dropdown settings page with all module dropdowns."""
    if not current_user.has_permission(UserRole.ADMIN):
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard.index'))

    # Define all modules with their dropdown configurations
    modules_config = [
        {
            'id': 'b2c_leads',
            'name': 'B2C Leads',
            'icon': 'bi-person-lines-fill',
            'color': 'primary',
            'groups': [
                {
                    'name': 'Source',
                    'display_name': 'Lead Sources',
                    'description': 'Sources where B2C leads come from',
                    'nested': False
                },
                {
                    'name': 'LeadStatus',
                    'display_name': 'Lead Status',
                    'description': 'Status options for B2C leads',
                    'nested': False
                }
            ]
        },
        {
            'id': 'b2b_leads',
            'name': 'B2B Leads',
            'icon': 'bi-building',
            'color': 'success',
            'groups': [
                {
                    'name': 'B2BLeadType',
                    'display_name': 'Lead Types',
                    'description': 'Types of B2B leads',
                    'nested': False
                },
                {
                    'name': 'B2BMeetingStatus',
                    'display_name': 'Meeting Status',
                    'description': 'Status options for B2B meetings',
                    'nested': False
                }
            ]
        },
        {
            'id': 'follow_ups',
            'name': 'Follow Ups',
            'icon': 'bi-calendar-check',
            'color': 'info',
            'groups': [
                {
                    'name': 'FollowUpOutcome',
                    'display_name': 'Follow-up Outcomes',
                    'description': 'Possible outcomes for follow-up activities',
                    'nested': False
                }
            ]
        },
        {
            'id': 'health_camps',
            'name': 'Health Camps',
            'icon': 'bi-heart-pulse',
            'color': 'danger',
            'groups': [
                {
                    'name': 'CampPackage',
                    'display_name': 'Camp Packages',
                    'description': 'Available health camp packages',
                    'nested': False
                }
            ]
        },
        {
            'id': 'customers',
            'name': 'Customers',
            'icon': 'bi-people',
            'color': 'secondary',
            'groups': []  # Customers mainly use references to other tables
        },
        {
            'id': 'employees',
            'name': 'Employees',
            'icon': 'bi-person-badge',
            'color': 'info',
            'groups': [
                {
                    'name': 'EmployeeType',
                    'display_name': 'Employment Types',
                    'description': 'Types of employment (Full-time, Part-time, etc.)',
                    'nested': False
                },
                {
                    'name': 'EmployeeDesignation',
                    'display_name': 'Designations',
                    'description': 'Job designations/titles',
                    'nested': False
                },
                {
                    'name': 'Gender',
                    'display_name': 'Gender Options',
                    'description': 'Gender options for employees',
                    'nested': False
                }
            ]
        },
        {
            'id': 'channel_partners',
            'name': 'Channel Partners',
            'icon': 'bi-diagram-3',
            'color': 'warning',
            'groups': []  # No dropdowns needed
        },
        {
            'id': 'services',
            'name': 'Services',
            'icon': 'bi-tools',
            'color': 'success',
            'groups': []  # Services are managed separately as master data
        },
        {
            'id': 'sales',
            'name': 'Sales',
            'icon': 'bi-cash-stack',
            'color': 'success',
            'groups': [
                {
                    'name': 'GSTType',
                    'display_name': 'GST Types',
                    'description': 'GST calculation types (Inclusive/Exclusive)',
                    'nested': False
                },
                {
                    'name': 'PaymentStatus',
                    'display_name': 'Payment Status',
                    'description': 'Payment status options',
                    'nested': False
                },
                {
                    'name': 'PaymentMethod',
                    'display_name': 'Payment Methods',
                    'description': 'Available payment methods',
                    'nested': False
                }
            ]
        },
        {
            'id': 'purchases',
            'name': 'Purchases',
            'icon': 'bi-cart',
            'color': 'primary',
            'groups': [
                {
                    'name': 'GSTType',
                    'display_name': 'GST Types',
                    'description': 'GST calculation types (Inclusive/Exclusive)',
                    'nested': False
                },
                {
                    'name': 'PaymentStatus',
                    'display_name': 'Payment Status',
                    'description': 'Payment status options',
                    'nested': False
                },
                {
                    'name': 'PaymentMethod',
                    'display_name': 'Payment Methods',
                    'description': 'Available payment methods',
                    'nested': False
                }
            ]
        },
        {
            'id': 'payments_received',
            'name': 'Payments Received',
            'icon': 'bi-arrow-down-circle',
            'color': 'success',
            'groups': [
                {
                    'name': 'PaymentMethod',
                    'display_name': 'Payment Methods',
                    'description': 'Available payment methods',
                    'nested': False
                },
                {
                    'name': 'TDSSection',
                    'display_name': 'TDS Sections',
                    'description': 'TDS section codes (194C, 194J, etc.)',
                    'nested': False
                }
            ]
        },
        {
            'id': 'payments_made',
            'name': 'Payments Made',
            'icon': 'bi-arrow-up-circle',
            'color': 'danger',
            'groups': [
                {
                    'name': 'PaymentMethod',
                    'display_name': 'Payment Methods',
                    'description': 'Available payment methods',
                    'nested': False
                },
                {
                    'name': 'TDSSection',
                    'display_name': 'TDS Sections',
                    'description': 'TDS section codes (194C, 194J, etc.)',
                    'nested': False
                },
                {
                    'name': 'PaymentCategory',
                    'display_name': 'Payment Categories',
                    'description': 'Categories for payments made',
                    'nested': False
                }
            ]
        },
        {
            'id': 'expenses',
            'name': 'Expenses',
            'icon': 'bi-receipt',
            'color': 'warning',
            'groups': [
                {
                    'name': 'ExpenseMainCategory',
                    'display_name': 'Expense Categories',
                    'description': 'Main expense categories',
                    'nested': True,
                    'child_group': 'ExpenseSubCategory'
                }
            ]
        }
    ]

    # Fetch all settings from database
    all_settings = Setting.query.order_by(Setting.group, Setting.sort_order).all()
    settings_by_group = {}
    for setting in all_settings:
        if setting.group not in settings_by_group:
            settings_by_group[setting.group] = []
        settings_by_group[setting.group].append(setting)

    # Build module dropdown data
    module_dropdowns = {}
    for module in modules_config:
        module_data = {
            'name': module['name'],
            'icon': module['icon'],
            'color': module['color'],
            'groups': []
        }
        
        for group_config in module['groups']:
            group_name = group_config['name']
            group_items = settings_by_group.get(group_name, [])
            
            # Process items
            items_list = []
            if group_config.get('nested'):
                # Handle nested dropdowns (like expenses)
                child_group = group_config.get('child_group')
                child_settings = settings_by_group.get(child_group, [])
                
                for item in group_items:
                    # Find children for this item
                    children = [
                        {
                            'id': child.id,
                            'key': child.key,
                            'value': child.value
                        }
                        for child in child_settings
                        if child.key.startswith(item.key + '_')
                    ]
                    
                    items_list.append({
                        'id': item.id,
                        'key': item.key,
                        'value': item.value,
                        'has_children': True,
                        'children': children,
                        'children_count': len(children)
                    })
            else:
                # Regular dropdowns
                items_list = [
                    {
                        'id': item.id,
                        'key': item.key,
                        'value': item.value,
                        'has_children': False
                    }
                    for item in group_items
                ]
            
            module_data['groups'].append({
                'name': group_name,
                'display_name': group_config['display_name'],
                'description': group_config.get('description', ''),
                'nested': group_config.get('nested', False),
                'child_group': group_config.get('child_group', ''),
                'items': items_list
            })
        
        module_dropdowns[module['id']] = module_data

    # Calculate dropdown count for each module
    for module in modules_config:
        module['dropdown_count'] = len(module['groups'])

    return render_template('settings/unified_dropdowns.html', 
                         title='Dropdown Settings',
                         modules=modules_config,
                         module_dropdowns=module_dropdowns)


@bp.route('/dropdowns/leads')
@login_required
def leads_dropdowns():
    """Manage lead-related dropdown settings."""
    if not current_user.has_permission(UserRole.ADMIN):
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard.index'))

    groups = ['Source', 'LeadStatus']
    settings_by_group = {}
    for group in groups:
        settings_by_group[group] = Setting.query.filter_by(group=group).order_by(Setting.sort_order).all()

    return render_template('settings/leads_dropdowns.html', title='Lead Settings', settings_by_group=settings_by_group)


@bp.route('/dropdowns/services')
@login_required
def services_dropdowns():
    """Manage service-related dropdown settings."""
    if not current_user.has_permission(UserRole.ADMIN):
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard.index'))

    groups = ['Services']
    settings_by_group = {}
    for group in groups:
        settings_by_group[group] = Setting.query.filter_by(group=group).order_by(Setting.sort_order).all()

    return render_template('settings/services_dropdowns.html', title='Service Settings', settings_by_group=settings_by_group)


@bp.route('/dropdowns/finance')
@login_required
def finance_dropdowns():
    """Manage finance-related dropdown settings."""
    if not current_user.has_permission(UserRole.ADMIN):
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard.index'))

    groups = ['ExpenseCategory']
    settings_by_group = {}
    for group in groups:
        settings_by_group[group] = Setting.query.filter_by(group=group).order_by(Setting.sort_order).all()

    return render_template('settings/finance_dropdowns.html', title='Finance Settings', settings_by_group=settings_by_group)


@bp.route('/dropdowns/hr')
@login_required
def hr_dropdowns():
    """Manage HR-related dropdown settings."""
    if not current_user.has_permission(UserRole.ADMIN):
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard.index'))

    groups = ['EmployeeType']
    settings_by_group = {}
    for group in groups:
        settings_by_group[group] = Setting.query.filter_by(group=group).order_by(Setting.sort_order).all()

    return render_template('settings/hr_dropdowns.html', title='HR Settings', settings_by_group=settings_by_group)


@bp.route('/dropdowns/camps')
@login_required
def camp_dropdowns():
    """Manage camp-related dropdown settings."""
    if not current_user.has_permission(UserRole.ADMIN):
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard.index'))

    camp_packages = Setting.query.filter_by(group='CampPackage').order_by(Setting.sort_order).all()

    return render_template('settings/camp_dropdowns.html', title='Camp Settings', camp_packages=camp_packages)


@bp.route('/dropdowns/expenses')
@login_required
def expense_dropdowns():
    """Manage expense category and sub-category settings."""
    if not current_user.has_permission(UserRole.ADMIN):
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard.index'))

    # Get main categories
    main_categories = Setting.query.filter_by(group='ExpenseMainCategory').order_by(Setting.sort_order).all()

    # Get sub-categories grouped by main category
    sub_categories = Setting.query.filter_by(group='ExpenseSubCategory').order_by(Setting.sort_order).all()
    sub_categories_by_main = {}

    # Get main category keys for matching
    main_category_keys = [cat.key for cat in main_categories]

    for sub_cat in sub_categories:
        # Find which main category this sub-category belongs to
        main_key = None
        for cat_key in main_category_keys:
            if sub_cat.key.startswith(cat_key + '_'):
                main_key = cat_key
                break

        if main_key:
            if main_key not in sub_categories_by_main:
                sub_categories_by_main[main_key] = []
            sub_categories_by_main[main_key].append(sub_cat)

    return render_template('settings/expense_dropdowns.html',
                         title='Expense Settings',
                         main_categories=main_categories,
                         sub_categories_by_main=sub_categories_by_main)


@bp.route('/dropdowns/add', methods=['POST'])
@login_required
def add_setting():
    """Add new setting item."""
    if not current_user.has_permission(UserRole.ADMIN):
        return jsonify({'success': False, 'message': 'Access denied'}), 403

    data = request.get_json()
    group = data.get('group')
    key = data.get('key')
    value = data.get('value')

    if not all([group, key, value]):
        return jsonify({'success': False, 'message': 'All fields required'}), 400

    # Check if key already exists in group
    existing = Setting.query.filter_by(group=group, key=key).first()
    if existing:
        return jsonify({'success': False, 'message': 'Key already exists'}), 400

    # Get max sort_order
    max_order = db.session.query(db.func.max(Setting.sort_order)).filter_by(group=group).scalar() or 0

    setting = Setting(
        group=group,
        key=key,
        value=value,
        sort_order=max_order + 1,
        is_active=True,
        created_by=current_user.id,
        updated_by=current_user.id
    )
    db.session.add(setting)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Setting added successfully'})


@bp.route('/dropdowns/<int:setting_id>/edit', methods=['POST'])
@login_required
def edit_setting(setting_id):
    """Edit setting item."""
    if not current_user.has_permission(UserRole.ADMIN):
        return jsonify({'success': False, 'message': 'Access denied'}), 403

    setting = Setting.query.get_or_404(setting_id)
    data = request.get_json()
    value = data.get('value')

    if not value:
        return jsonify({'success': False, 'message': 'Value required'}), 400

    setting.value = value
    setting.updated_by = current_user.id
    db.session.commit()

    return jsonify({'success': True, 'message': 'Setting updated successfully'})


@bp.route('/dropdowns/<int:setting_id>/delete', methods=['POST'])
@login_required
def delete_setting(setting_id):
    """Delete setting item."""
    if not current_user.has_permission(UserRole.ADMIN):
        return jsonify({'success': False, 'message': 'Access denied'}), 403

    setting = Setting.query.get_or_404(setting_id)

    # Check if setting is in use
    if setting.group == 'LeadStatus':
        count = B2CLead.query.filter_by(status=setting.key).count()
        if count > 0:
            return jsonify({'success': False, 'message': f'Cannot delete: {count} leads use this status'}), 400

    db.session.delete(setting)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Setting deleted successfully'})


@bp.route('/dropdowns/expense-subcategories/<category_key>')
@login_required
def get_expense_subcategories(category_key):
    """Get sub-categories for a specific expense main category."""
    if not current_user.has_permission(UserRole.ADMIN):
        return jsonify({'error': 'Access denied'}), 403

    from app.models import Setting
    sub_categories = Setting.query.filter(
        Setting.group == 'ExpenseSubCategory',
        Setting.key.like(f'{category_key}_%')
    ).order_by(Setting.sort_order).all()

    return jsonify([{'key': s.key, 'value': s.value} for s in sub_categories])


@bp.route('/users')
@login_required
def users():
    """User management page."""
    if not current_user.has_permission(UserRole.ADMIN):
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard.index'))

    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('settings/users.html', title='User Management', users=users)


@bp.route('/users/create', methods=['GET', 'POST'])
@login_required
def create_user():
    """Create new user."""
    if not current_user.has_permission(UserRole.ADMIN):
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard.index'))

    form = UserForm()
    if form.validate_on_submit():
        # Collect selected modules
        allowed_modules = []
        if form.dashboard_access.data:
            allowed_modules.append('dashboard')
        if form.leads_b2c_access.data:
            allowed_modules.append('leads_b2c')
        if form.leads_b2b_access.data:
            allowed_modules.append('leads_b2b')
        if form.follow_ups_access.data:
            allowed_modules.append('follow_ups')
        if form.customers_access.data:
            allowed_modules.append('customers')
        if form.employees_access.data:
            allowed_modules.append('employees')
        if form.expenses_access.data:
            allowed_modules.append('expenses')
        if form.channel_partners_access.data:
            allowed_modules.append('channel_partners')
        if form.services_access.data:
            allowed_modules.append('services')
        if form.camps_access.data:
            allowed_modules.append('camps')
        if form.finance_access.data:
            allowed_modules.append('finance')

        user = User(
            full_name=form.full_name.data,
            email=form.email.data,
            role=UserRole[form.role.data],
            is_active=form.is_active.data,
            created_by=current_user.id,
            updated_by=current_user.id
        )
        user.allowed_modules = allowed_modules
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash(f'User {user.full_name} created successfully!', 'success')
        return redirect(url_for('settings.users'))

    return render_template('settings/create_user.html', title='Create User', form=form)


@bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    """Edit user."""
    if not current_user.has_permission(UserRole.ADMIN):
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard.index'))

    user = User.query.get_or_404(user_id)

    # Prevent editing other admins
    if user.role == UserRole.ADMIN and user.id != current_user.id:
        flash('Cannot edit other admin users.', 'error')
        return redirect(url_for('settings.users'))

    form = EditUserForm(original_email=user.email, obj=user)

    if form.validate_on_submit():
        # Collect selected modules
        allowed_modules = []
        if form.dashboard_access.data:
            allowed_modules.append('dashboard')
        if form.leads_b2c_access.data:
            allowed_modules.append('leads_b2c')
        if form.leads_b2b_access.data:
            allowed_modules.append('leads_b2b')
        if form.follow_ups_access.data:
            allowed_modules.append('follow_ups')
        if form.customers_access.data:
            allowed_modules.append('customers')
        if form.employees_access.data:
            allowed_modules.append('employees')
        if form.expenses_access.data:
            allowed_modules.append('expenses')
        if form.channel_partners_access.data:
            allowed_modules.append('channel_partners')
        if form.services_access.data:
            allowed_modules.append('services')
        if form.camps_access.data:
            allowed_modules.append('camps')
        if form.finance_access.data:
            allowed_modules.append('finance')

        form.populate_obj(user)
        user.role = UserRole[form.role.data]
        user.allowed_modules = allowed_modules
        user.updated_by = current_user.id
        db.session.commit()

        flash(f'User {user.full_name} updated successfully!', 'success')
        return redirect(url_for('settings.users'))

    # Set form values for GET request
    form.role.data = user.role.value
    form.is_active.data = user.is_active

    # Set module permissions checkboxes
    allowed = user.allowed_modules
    form.dashboard_access.data = 'dashboard' in allowed
    form.leads_b2c_access.data = 'leads_b2c' in allowed
    form.leads_b2b_access.data = 'leads_b2b' in allowed
    form.follow_ups_access.data = 'follow_ups' in allowed
    form.customers_access.data = 'customers' in allowed
    form.employees_access.data = 'employees' in allowed
    form.expenses_access.data = 'expenses' in allowed
    form.channel_partners_access.data = 'channel_partners' in allowed
    form.services_access.data = 'services' in allowed
    form.camps_access.data = 'camps' in allowed
    form.finance_access.data = 'finance' in allowed

    return render_template('settings/edit_user.html', title='Edit User', form=form, user=user)


@bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
def toggle_user_status(user_id):
    """Toggle user active status."""
    if not current_user.has_permission(UserRole.ADMIN):
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard.index'))

    user = User.query.get_or_404(user_id)

    # Prevent deactivating other admins
    if user.role == UserRole.ADMIN and user.id != current_user.id:
        flash('Cannot deactivate other admin users.', 'error')
        return redirect(url_for('settings.users'))

    user.is_active = not user.is_active
    user.updated_by = current_user.id
    db.session.commit()

    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.full_name} has been {status}.', 'success')
    return redirect(url_for('settings.users'))


@bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
def reset_user_password(user_id):
    """Reset user password to a default one."""
    if not current_user.has_permission(UserRole.ADMIN):
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard.index'))

    user = User.query.get_or_404(user_id)

    # Generate a default password
    default_password = f"Welcome@{user_id}"
    user.set_password(default_password)
    user.updated_by = current_user.id
    db.session.commit()

    flash(f'Password for {user.full_name} has been reset to: {default_password}', 'success')
    return redirect(url_for('settings.users'))


@bp.route('/delete-all-data', methods=['POST'])
@login_required
def delete_all_data():
    """Delete all application data (admin only)."""
    if not current_user.has_permission(UserRole.ADMIN):
        return jsonify({
            'success': False,
            'message': 'Access denied. Admin privileges required.'
        }), 403

    # Validate CSRF token from JSON data
    data = request.get_json() or {}
    csrf_token = data.get('csrf_token')
    if not csrf_token:
        return jsonify({
            'success': False,
            'message': 'CSRF token missing.'
        }), 400

    try:
        validate_csrf(csrf_token)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'CSRF validation failed.'
        }), 400

    try:
        # Delete in order to respect foreign key constraints
        # Start with dependent records first
        AuditLog.query.delete()
        FollowUp.query.delete()
        Expense.query.delete()
        Customer.query.delete()
        B2CLead.query.delete()
        B2BLead.query.delete()
        Employee.query.delete()
        ChannelPartner.query.delete()
        Service.query.delete()
        Setting.query.delete()

        # Delete all users except admin users
        User.query.filter(User.role != UserRole.ADMIN).delete()

        # Commit the changes
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'All application data and non-admin user profiles have been successfully deleted.'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to delete data: {str(e)}'
        }), 500