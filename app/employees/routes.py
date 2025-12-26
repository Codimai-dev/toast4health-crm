"""Employees routes."""

import os
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app import db, require_module_access
from app.employees import bp
from app.employees.forms import EmployeeForm
from app.models import (
    Employee, Attendance, Leave, Task, PerformanceMetric,
    AttendanceStatus, LeaveType, LeaveStatus, TaskStatus, TaskPriority
)


def save_uploaded_file(file_field, upload_folder, filename_prefix=""):
    """Save uploaded file and return the relative path."""
    if file_field.data:
        filename = secure_filename(file_field.data.filename)
        if filename_prefix:
            filename = f"{filename_prefix}_{filename}"
        file_path = os.path.join(current_app.root_path, 'static', upload_folder, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file_field.data.save(file_path)
        return f"{upload_folder}/{filename}"
    return None


@bp.route('/')
@login_required
@require_module_access('employees')
def index():
    """Display all employees."""
    # Use raw SQL to handle empty gender values
    from sqlalchemy import text

    class SimpleEmployee:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    employees = db.session.execute(
        text("""
            SELECT id, employee_code, employ_type, name, contact_no, dob, degree,
                   temporary_address, permanent_address, employ_image, aadhar_no,
                   total_experience, skill_set, gender, designation, whatsapp_no,
                   email, pdf_link, bank_name, branch_name, account_no, ifsc_code,
                   created_at, updated_at, created_by, updated_by
            FROM employee
            ORDER BY created_at DESC
        """)
    ).fetchall()

    # Convert to employee objects and handle gender
    employee_objects = []
    for row in employees:
        # Convert row to dictionary properly
        employee_dict = {column: value for column, value in row._mapping.items()}
        # Handle empty gender values
        if employee_dict['gender'] == '' or employee_dict['gender'] is None:
            employee_dict['gender'] = None
        # Create a simple object for template use
        employee_obj = SimpleEmployee(**employee_dict)
        employee_objects.append(employee_obj)

    return render_template('employees/index.html', title='Employees', employees=employee_objects)


@bp.route('/add', methods=['GET', 'POST'])
@login_required
@require_module_access('employees')
def add():
    """Add a new employee."""
    form = EmployeeForm()
    form.employee_code.data = Employee.generate_employee_code()
    if form.validate_on_submit():
        try:
            # Handle file uploads
            pdf_path = save_uploaded_file(form.pdf_file, 'uploads/pdfs', f"emp_{form.employee_code.data}")
            image_path = save_uploaded_file(form.employ_image_file, 'uploads/images', f"emp_{form.employee_code.data}")

            # Use uploaded file path if available, otherwise use URL
            final_pdf_link = pdf_path if pdf_path else form.pdf_link.data
            final_employ_image = image_path if image_path else form.employ_image.data

            employee = Employee(
                employee_code=form.employee_code.data,
                name=form.name.data,
                contact_no=form.contact_no.data,
                email=form.email.data,
                designation=form.designation.data,
                employ_type=form.employ_type.data,
                gender=form.gender.data if form.gender.data and form.gender.data != '' else None,
                dob=form.dob.data,
                degree=form.degree.data,
                total_experience=form.total_experience.data,
                whatsapp_no=form.whatsapp_no.data,
                aadhar_no=form.aadhar_no.data,
                bank_name=form.bank_name.data,
                branch_name=form.branch_name.data,
                account_no=form.account_no.data,
                ifsc_code=form.ifsc_code.data,
                temporary_address=form.temporary_address.data,
                permanent_address=form.permanent_address.data,
                skill_set=form.skill_set.data,
                pdf_link=final_pdf_link,
                employ_image=final_employ_image,
                created_by=current_user.id,
                updated_by=current_user.id
            )
            db.session.add(employee)
            db.session.commit()
            flash('Employee added successfully!', 'success')
            return redirect(url_for('employees.index'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error adding employee: {str(e)}')
            
            # Provide user-friendly error messages
            error_message = 'Failed to add employee. '
            if 'unique constraint' in str(e).lower() or 'duplicate' in str(e).lower():
                if 'employee_code' in str(e).lower():
                    error_message += 'Employee code already exists. Please try again with a different code.'
                elif 'email' in str(e).lower():
                    error_message += 'Email address already exists. Please use a different email.'
                elif 'contact' in str(e).lower():
                    error_message += 'Contact number already exists. Please use a different contact number.'
                else:
                    error_message += 'A duplicate value was found. Please check your input.'
            elif 'foreign key' in str(e).lower():
                error_message += 'Invalid reference to another record. Please check your selections.'
            elif 'not null' in str(e).lower() or 'null value' in str(e).lower():
                error_message += 'Required field is missing. Please fill in all required fields.'
            elif 'file' in str(e).lower() or 'upload' in str(e).lower():
                error_message += 'File upload failed. Please check the file type and size.'
            else:
                error_message += f'Please check your input and try again. Error: {str(e)}'
            
            flash(error_message, 'error')
    elif request.method == 'POST' and not form.validate():
        # Display validation errors
        flash('Please correct the errors in the form below.', 'error')
    
    return render_template('employees/add.html', title='Add Employee', form=form)


@bp.route('/view/<int:id>')
@login_required
@require_module_access('employees')
def view(id):
    """View an employee."""
    # Use raw SQL to handle empty gender values
    from sqlalchemy import text

    class SimpleEmployee:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    result = db.session.execute(
        text("""
            SELECT id, employee_code, employ_type, name, contact_no, dob, degree,
                   temporary_address, permanent_address, employ_image, aadhar_no,
                   total_experience, skill_set, gender, designation, whatsapp_no,
                   email, pdf_link, bank_name, branch_name, account_no, ifsc_code,
                   created_at, updated_at, created_by, updated_by
            FROM employee
            WHERE id = :id
        """),
        {'id': id}
    ).fetchone()

    if not result:
        from flask import abort
        abort(404)

    # Convert result to dictionary properly
    employee_dict = {column: value for column, value in result._mapping.items()}
    # Handle empty gender values
    if employee_dict['gender'] == '' or employee_dict['gender'] is None:
        employee_dict['gender'] = None

    # Convert date string back to datetime object for WTForms
    if employee_dict['dob'] and isinstance(employee_dict['dob'], str):
        from datetime import datetime
        try:
            employee_dict['dob'] = datetime.strptime(employee_dict['dob'], '%Y-%m-%d').date()
        except ValueError:
            employee_dict['dob'] = None

    # Create a simple object for template use
    employee = SimpleEmployee(**employee_dict)

    return render_template('employees/view.html', title='View Employee', employee=employee)


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@require_module_access('employees')
def edit(id):
    """Edit an employee."""
    # Use raw SQL to handle empty gender values
    from sqlalchemy import text

    class SimpleEmployee:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    result = db.session.execute(
        text("""
            SELECT id, employee_code, employ_type, name, contact_no, dob, degree,
                   temporary_address, permanent_address, employ_image, aadhar_no,
                   total_experience, skill_set, gender, designation, whatsapp_no,
                   email, pdf_link, bank_name, branch_name, account_no, ifsc_code,
                   created_at, updated_at, created_by, updated_by
            FROM employee
            WHERE id = :id
        """),
        {'id': id}
    ).fetchone()

    if not result:
        from flask import abort
        abort(404)

    employee_dict = {column: value for column, value in result._mapping.items()}
    # Handle empty gender values
    if employee_dict['gender'] == '' or employee_dict['gender'] is None:
        employee_dict['gender'] = None

    # Convert date string back to datetime object for WTForms
    if employee_dict['dob'] and isinstance(employee_dict['dob'], str):
        from datetime import datetime
        try:
            employee_dict['dob'] = datetime.strptime(employee_dict['dob'], '%Y-%m-%d').date()
        except ValueError:
            employee_dict['dob'] = None

    # Create a simple object for template use
    employee = SimpleEmployee(**employee_dict)

    # Populate form with converted data
    form = EmployeeForm()
    if request.method == 'GET':
        form.employee_code.data = employee_dict['employee_code']
        form.name.data = employee_dict['name']
        form.contact_no.data = employee_dict['contact_no']
        form.email.data = employee_dict['email']
        form.designation.data = employee_dict['designation']
        form.employ_type.data = employee_dict['employ_type']
        form.gender.data = employee_dict['gender'] if employee_dict['gender'] else ''
        form.dob.data = employee_dict['dob']
        form.degree.data = employee_dict['degree']
        form.total_experience.data = employee_dict['total_experience']
        form.whatsapp_no.data = employee_dict['whatsapp_no']
        form.aadhar_no.data = employee_dict['aadhar_no']
        form.bank_name.data = employee_dict['bank_name']
        form.branch_name.data = employee_dict['branch_name']
        form.account_no.data = employee_dict['account_no']
        form.ifsc_code.data = employee_dict['ifsc_code']
        form.temporary_address.data = employee_dict['temporary_address']
        form.permanent_address.data = employee_dict['permanent_address']
        form.skill_set.data = employee_dict['skill_set']
        form.pdf_link.data = employee_dict['pdf_link']
        form.employ_image.data = employee_dict['employ_image']

    if form.validate_on_submit():
        try:
            # Handle file uploads
            pdf_path = save_uploaded_file(form.pdf_file, 'uploads/pdfs', f"emp_{form.employee_code.data}")
            image_path = save_uploaded_file(form.employ_image_file, 'uploads/images', f"emp_{form.employee_code.data}")

            # Use uploaded file path if available, otherwise use URL
            final_pdf_link = pdf_path if pdf_path else form.pdf_link.data
            final_employ_image = image_path if image_path else form.employ_image.data

            # Update the database using raw SQL
            update_data = {
                'employee_code': form.employee_code.data,
                'name': form.name.data,
                'contact_no': form.contact_no.data,
                'email': form.email.data,
                'designation': form.designation.data,
                'employ_type': form.employ_type.data,
                'gender': form.gender.data if form.gender.data and form.gender.data != '' else None,
                'dob': form.dob.data.isoformat() if form.dob.data else None,  # Convert date to ISO format for SQL
                'degree': form.degree.data,
                'total_experience': form.total_experience.data,
                'whatsapp_no': form.whatsapp_no.data,
                'aadhar_no': form.aadhar_no.data,
                'bank_name': form.bank_name.data,
                'branch_name': form.branch_name.data,
                'account_no': form.account_no.data,
                'ifsc_code': form.ifsc_code.data,
                'temporary_address': form.temporary_address.data,
                'permanent_address': form.permanent_address.data,
                'skill_set': form.skill_set.data,
                'pdf_link': final_pdf_link,
                'employ_image': final_employ_image,
                'updated_by': current_user.id
            }

            # Build the UPDATE query dynamically
            set_parts = []
            for key in update_data.keys():
                if update_data[key] is not None:
                    set_parts.append(f"{key} = :{key}")
                else:
                    set_parts.append(f"{key} = NULL")

            update_query = f"""
                UPDATE employee
                SET {', '.join(set_parts)}
                WHERE id = :id
            """
            update_data['id'] = id

            db.session.execute(text(update_query), update_data)
            db.session.commit()
            flash('Employee updated successfully!', 'success')
            return redirect(url_for('employees.index'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error updating employee: {str(e)}')
            
            # Provide user-friendly error messages
            error_message = 'Failed to update employee. '
            if 'unique constraint' in str(e).lower() or 'duplicate' in str(e).lower():
                if 'employee_code' in str(e).lower():
                    error_message += 'Employee code already exists. Please use a different code.'
                elif 'email' in str(e).lower():
                    error_message += 'Email address already exists. Please use a different email.'
                elif 'contact' in str(e).lower():
                    error_message += 'Contact number already exists. Please use a different contact number.'
                else:
                    error_message += 'A duplicate value was found. Please check your input.'
            elif 'foreign key' in str(e).lower():
                error_message += 'Invalid reference to another record. Please check your selections.'
            elif 'not null' in str(e).lower() or 'null value' in str(e).lower():
                error_message += 'Required field is missing. Please fill in all required fields.'
            elif 'file' in str(e).lower() or 'upload' in str(e).lower():
                error_message += 'File upload failed. Please check the file type and size.'
            else:
                error_message += f'Please check your input and try again. Error: {str(e)}'
            
            flash(error_message, 'error')
    elif request.method == 'POST' and not form.validate():
        # Display validation errors
        flash('Please correct the errors in the form below.', 'error')
    
    return render_template('employees/edit.html', title='Edit Employee', form=form, employee=employee)


# Attendance Routes
@bp.route('/attendance')
@login_required
@require_module_access('employees')
def attendance():
    """Display attendance records."""
    from datetime import date, timedelta

    # Get current month
    today = date.today()
    start_of_month = today.replace(day=1)

    # Get all employees with their attendance for current month
    employees = Employee.query.all()
    attendance_data = []

    for employee in employees:
        monthly_attendance = Attendance.query.filter(
            Attendance.employee_id == employee.id,
            Attendance.date >= start_of_month,
            Attendance.date <= today
        ).all()

        present_days = sum(1 for a in monthly_attendance if a.status == AttendanceStatus.PRESENT)
        total_days = len(monthly_attendance)

        attendance_data.append({
            'employee': employee,
            'attendance': monthly_attendance,
            'present_days': present_days,
            'total_days': total_days,
            'percentage': (present_days / total_days * 100) if total_days > 0 else 0
        })

    return render_template('employees/attendance.html', title='Attendance Management',
                         attendance_data=attendance_data, today=today)


@bp.route('/attendance/mark', methods=['POST'])
@login_required
@require_module_access('employees')
def mark_attendance():
    """Mark attendance for an employee."""
    from datetime import date, datetime

    employee_id = request.form.get('employee_id')
    if not employee_id:
        flash('Employee not selected!', 'error')
        return redirect(url_for('employees.attendance'))

    employee = Employee.query.get_or_404(int(employee_id))
    attendance_date = date.today()

    # Check if attendance already marked
    existing = Attendance.query.filter_by(
        employee_id=employee_id,
        date=attendance_date
    ).first()

    if existing:
        flash(f'Attendance already marked for {employee.name} today!', 'warning')
        return redirect(url_for('employees.attendance'))

    # Get form data
    status = request.form.get('status', 'PRESENT')
    check_in = request.form.get('check_in')
    check_out = request.form.get('check_out')
    notes = request.form.get('notes')

    attendance = Attendance(
        employee_id=employee_id,
        date=attendance_date,
        status=AttendanceStatus[status],
        check_in_time=datetime.strptime(check_in, '%H:%M').time() if check_in else None,
        check_out_time=datetime.strptime(check_out, '%H:%M').time() if check_out else None,
        notes=notes,
        created_by=current_user.id,
        updated_by=current_user.id
    )

    # Calculate working hours if both times provided
    if attendance.check_in_time and attendance.check_out_time:
        from datetime import datetime, date
        check_in_dt = datetime.combine(date.today(), attendance.check_in_time)
        check_out_dt = datetime.combine(date.today(), attendance.check_out_time)
        hours = (check_out_dt - check_in_dt).total_seconds() / 3600
        attendance.working_hours = round(hours, 2)

    db.session.add(attendance)
    db.session.commit()

    flash(f'Attendance marked for {employee.name}!', 'success')
    return redirect(url_for('employees.attendance'))


# Leave Management Routes
@bp.route('/leave')
@login_required
@require_module_access('employees')
def leave():
    """Display leave requests."""
    leave_requests = Leave.query.order_by(Leave.created_at.desc()).all()
    return render_template('employees/leave.html', title='Leave Management', leave_requests=leave_requests)


@bp.route('/leave/apply', methods=['GET', 'POST'])
@login_required
@require_module_access('employees')
def apply_leave():
    """Apply for leave."""
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        leave_type = request.form.get('leave_type')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        reason = request.form.get('reason')

        from datetime import datetime
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        days = (end - start).days + 1

        leave_request = Leave(
            employee_id=employee_id,
            leave_type=LeaveType[leave_type],
            start_date=start,
            end_date=end,
            days_requested=days,
            reason=reason,
            created_by=current_user.id,
            updated_by=current_user.id
        )

        db.session.add(leave_request)
        db.session.commit()

        flash('Leave application submitted successfully!', 'success')
        return redirect(url_for('employees.leave'))

    employees = Employee.query.all()
    return render_template('employees/apply_leave.html', title='Apply for Leave', employees=employees)


@bp.route('/leave/approve/<int:leave_id>', methods=['POST'])
@login_required
@require_module_access('employees')
def approve_leave(leave_id):
    """Approve or reject leave request."""
    leave_request = Leave.query.get_or_404(leave_id)
    action = request.form.get('action')

    if action == 'approve':
        leave_request.status = LeaveStatus.APPROVED
        leave_request.approved_by = current_user.id
        leave_request.approved_at = datetime.utcnow()
        flash('Leave approved!', 'success')
    elif action == 'reject':
        leave_request.status = LeaveStatus.REJECTED
        leave_request.approved_by = current_user.id
        leave_request.approved_at = datetime.utcnow()
        comments = request.form.get('comments')
        if comments:
            leave_request.comments = comments
        flash('Leave rejected!', 'warning')

    db.session.commit()
    return redirect(url_for('employees.leave'))


# Task Management Routes
@bp.route('/tasks')
@login_required
@require_module_access('employees')
def tasks():
    """Display all tasks."""
    from datetime import date
    all_tasks = Task.query.order_by(Task.created_at.desc()).all()
    return render_template('employees/tasks.html', title='Task Management', tasks=all_tasks, date=date)


@bp.route('/tasks/assign', methods=['GET', 'POST'])
@login_required
@require_module_access('employees')
def assign_task():
    """Assign a new task."""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        assigned_to = request.form.get('assigned_to')
        priority = request.form.get('priority', 'MEDIUM')
        due_date = request.form.get('due_date')

        task = Task(
            title=title,
            description=description,
            assigned_to=assigned_to,
            assigned_by=current_user.id,
            priority=TaskPriority[priority],
            due_date=datetime.strptime(due_date, '%Y-%m-%d').date() if due_date else None,
            created_by=current_user.id,
            updated_by=current_user.id
        )

        db.session.add(task)
        db.session.commit()

        flash('Task assigned successfully!', 'success')
        return redirect(url_for('employees.tasks'))

    employees = Employee.query.all()
    return render_template('employees/assign_task.html', title='Assign Task', employees=employees)


@bp.route('/tasks/update/<int:task_id>', methods=['POST'])
@login_required
@require_module_access('employees')
def update_task(task_id):
    """Update task status."""
    task = Task.query.get_or_404(task_id)
    status = request.form.get('status')

    task.status = TaskStatus[status]
    if status == 'COMPLETED':
        task.completed_at = datetime.utcnow()

    task.updated_by = current_user.id
    db.session.commit()

    flash('Task updated successfully!', 'success')
    return redirect(url_for('employees.tasks'))


# Performance Routes
@bp.route('/performance')
@login_required
@require_module_access('employees')
def performance():
    """Display employee performance metrics."""
    from datetime import date, timedelta

    # Get current month metrics
    today = date.today()
    start_of_month = today.replace(day=1)

    employees = Employee.query.all()
    performance_data = []

    for employee in employees:
        # Get current month metrics
        monthly_metrics = PerformanceMetric.query.filter(
            PerformanceMetric.employee_id == employee.id,
            PerformanceMetric.metric_date >= start_of_month
        ).first()

        # Calculate some basic metrics if not available
        if not monthly_metrics:
            # Calculate from actual data
            leads_assigned = len(employee.assigned_tasks)  # This is approximate
            tasks_completed = Task.query.filter(
                Task.assigned_to == employee.id,
                Task.status == TaskStatus.COMPLETED,
                Task.completed_at >= start_of_month
            ).count()

            monthly_metrics = PerformanceMetric(
                employee_id=employee.id,
                metric_date=today,
                leads_assigned=leads_assigned,
                tasks_completed=tasks_completed
            )
            db.session.add(monthly_metrics)
            db.session.commit()

        performance_data.append({
            'employee': employee,
            'metrics': monthly_metrics
        })

    return render_template('employees/performance.html', title='Performance Monitoring',
                         performance_data=performance_data)
