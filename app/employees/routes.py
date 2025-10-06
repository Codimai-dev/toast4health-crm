"""Employees routes."""

import os
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app import db, require_module_access
from app.employees import bp
from app.employees.forms import EmployeeForm
from app.models import Employee


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

        try:
            db.session.execute(text(update_query), update_data)
            db.session.commit()
            flash('Employee updated successfully!', 'success')
            return redirect(url_for('employees.index'))
        except Exception as e:
            print("Database error:", str(e))
            db.session.rollback()
            flash('Error updating employee!', 'error')
    return render_template('employees/edit.html', title='Edit Employee', form=form, employee=employee)







