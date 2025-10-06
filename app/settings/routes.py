"""Settings routes."""

from flask import render_template, jsonify, flash, redirect, url_for, request
from flask_login import login_required, current_user
from flask_wtf.csrf import validate_csrf, generate_csrf
from app import db
from app.models import (
    User, UserRole, B2CLead, B2BLead, FollowUp, Customer, Booking,
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
    bookings_access = BooleanField('Bookings', render_kw={'class': 'form-check-input'})
    employees_access = BooleanField('Employees', render_kw={'class': 'form-check-input'})
    expenses_access = BooleanField('Expenses', render_kw={'class': 'form-check-input'})
    channel_partners_access = BooleanField('Channel Partners', render_kw={'class': 'form-check-input'})
    services_access = BooleanField('Services', render_kw={'class': 'form-check-input'})

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
    bookings_access = BooleanField('Bookings', render_kw={'class': 'form-check-input'})
    employees_access = BooleanField('Employees', render_kw={'class': 'form-check-input'})
    expenses_access = BooleanField('Expenses', render_kw={'class': 'form-check-input'})
    channel_partners_access = BooleanField('Channel Partners', render_kw={'class': 'form-check-input'})
    services_access = BooleanField('Services', render_kw={'class': 'form-check-input'})

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
    """Dropdown settings overview page."""
    if not current_user.has_permission(UserRole.ADMIN):
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard.index'))

    return render_template('settings/dropdowns.html', title='Dropdown Settings')


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
        if form.bookings_access.data:
            allowed_modules.append('bookings')
        if form.employees_access.data:
            allowed_modules.append('employees')
        if form.expenses_access.data:
            allowed_modules.append('expenses')
        if form.channel_partners_access.data:
            allowed_modules.append('channel_partners')
        if form.services_access.data:
            allowed_modules.append('services')

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
        if form.bookings_access.data:
            allowed_modules.append('bookings')
        if form.employees_access.data:
            allowed_modules.append('employees')
        if form.expenses_access.data:
            allowed_modules.append('expenses')
        if form.channel_partners_access.data:
            allowed_modules.append('channel_partners')
        if form.services_access.data:
            allowed_modules.append('services')

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
    form.bookings_access.data = 'bookings' in allowed
    form.employees_access.data = 'employees' in allowed
    form.expenses_access.data = 'expenses' in allowed
    form.channel_partners_access.data = 'channel_partners' in allowed
    form.services_access.data = 'services' in allowed

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
        Booking.query.delete()
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