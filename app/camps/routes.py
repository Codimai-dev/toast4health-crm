"""Camp routes."""

from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user

from app import db, require_module_access
from app.camps import bp
from app.camps.forms import CampForm
from app.models import Camp, CampDefault, UserRole


@bp.route('/')
@login_required
@require_module_access('camps')
def index():
    """Display all camp entries."""
    camps = Camp.query.order_by(Camp.camp_date.desc(), Camp.created_at.desc()).all()
    return render_template('camps/index.html', title='Health Camps', camps=camps)


@bp.route('/add', methods=['GET', 'POST'])
@login_required
@require_module_access('camps')
def add():
    """Add a new camp entry."""
    form = CampForm()
    
    # Load predefined defaults if available
    camp_default = CampDefault.get_active_default()
    
    # Use predefined camp_id if available, otherwise generate new one
    if request.method == 'GET':
        if camp_default and camp_default.camp_id:
            form.camp_id.data = camp_default.camp_id
        else:
            form.camp_id.data = Camp.generate_camp_id()
            
        # Load other predefined defaults
        if camp_default:
            if camp_default.staff_id:
                form.t4h_staff.data = str(camp_default.staff_id)
            if camp_default.camp_date:
                form.camp_date.data = camp_default.camp_date
            if camp_default.camp_location:
                form.camp_location.data = camp_default.camp_location
            if camp_default.org_name:
                form.org_name.data = camp_default.org_name
            if camp_default.package:
                form.package.data = camp_default.package
            if camp_default.diagnostic_partner:
                form.diagnostic_partner.data = camp_default.diagnostic_partner
    
    if form.validate_on_submit():
        # Use the camp_id from the form (which can be edited by user)
        camp = Camp(
            camp_id=form.camp_id.data,
            staff_id=int(form.t4h_staff.data) if form.t4h_staff.data else None,
            camp_date=form.camp_date.data,
            camp_location=form.camp_location.data,
            org_name=form.org_name.data,
            package=form.package.data,
            diagnostic_partner=form.diagnostic_partner.data,
            patient_name=form.patient_name.data,
            age=form.age.data,
            gender=form.gender.data if form.gender.data else None,
            test_done=form.test_done.data,
            phone_no=form.phone_no.data,
            created_by=current_user.id,
            updated_by=current_user.id
        )
        db.session.add(camp)
        db.session.commit()
        flash('Camp entry added successfully!', 'success')
        return redirect(url_for('camps.index'))
    
    # Check if user is admin
    is_admin = current_user.role == UserRole.ADMIN
    
    return render_template('camps/add.html', title='Add Camp Entry', form=form, 
                         is_admin=is_admin, has_default=camp_default is not None)


@bp.route('/view/<camp_id>')
@login_required
@require_module_access('camps')
def view(camp_id):
    """View a camp entry."""
    camp = Camp.query.filter_by(camp_id=camp_id).first_or_404()
    return render_template('camps/view.html', title='View Camp Entry', camp=camp)


@bp.route('/edit/<camp_id>', methods=['GET', 'POST'])
@login_required
@require_module_access('camps')
def edit(camp_id):
    """Edit a camp entry."""
    camp = Camp.query.filter_by(camp_id=camp_id).first_or_404()
    form = CampForm(obj=camp)
    
    if request.method == 'GET':
        # Pre-populate form with existing data
        form.camp_id.data = camp.camp_id
        form.t4h_staff.data = str(camp.staff_id) if camp.staff_id else ''
        form.camp_date.data = camp.camp_date
        form.camp_location.data = camp.camp_location
        form.org_name.data = camp.org_name
        form.package.data = camp.package
        form.diagnostic_partner.data = camp.diagnostic_partner
        form.patient_name.data = camp.patient_name
        form.age.data = camp.age
        form.gender.data = camp.gender
        form.test_done.data = camp.test_done
        form.phone_no.data = camp.phone_no
    
    if form.validate_on_submit():
        camp.staff_id = int(form.t4h_staff.data) if form.t4h_staff.data else None
        camp.camp_date = form.camp_date.data
        camp.camp_location = form.camp_location.data
        camp.org_name = form.org_name.data
        camp.package = form.package.data
        camp.diagnostic_partner = form.diagnostic_partner.data
        camp.patient_name = form.patient_name.data
        camp.age = form.age.data
        camp.gender = form.gender.data if form.gender.data else None
        camp.test_done = form.test_done.data
        camp.phone_no = form.phone_no.data
        camp.updated_by = current_user.id
        
        db.session.commit()
        flash('Camp entry updated successfully!', 'success')
        return redirect(url_for('camps.index'))
    
    return render_template('camps/edit.html', title='Edit Camp Entry', form=form, camp=camp)


@bp.route('/delete/<camp_id>', methods=['POST'])
@login_required
@require_module_access('camps')
def delete(camp_id):
    """Delete a camp entry."""
    camp = Camp.query.filter_by(camp_id=camp_id).first_or_404()
    db.session.delete(camp)
    db.session.commit()
    flash('Camp entry deleted successfully!', 'success')
    return redirect(url_for('camps.index'))


@bp.route('/predefine', methods=['POST'])
@login_required
@require_module_access('camps')
def predefine():
    """Predefine camp information (Admin only)."""
    from datetime import datetime
    
    # Check if user is admin
    if current_user.role != UserRole.ADMIN:
        flash('Only administrators can predefine camp information.', 'danger')
        return redirect(url_for('camps.add'))
    
    # Clear any existing active defaults
    CampDefault.clear_all_defaults()
    
    # Parse the camp_date string to a date object
    camp_date_str = request.form.get('camp_date')
    camp_date_obj = None
    if camp_date_str:
        try:
            # Parse the date string (format: YYYY-MM-DD)
            camp_date_obj = datetime.strptime(camp_date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            flash('Invalid date format. Please use YYYY-MM-DD format.', 'danger')
            return redirect(url_for('camps.add'))
    
    # Create new default
    camp_default = CampDefault(
        camp_id=request.form.get('camp_id') if request.form.get('camp_id') else None,
        staff_id=int(request.form.get('t4h_staff')) if request.form.get('t4h_staff') else None,
        camp_date=camp_date_obj,
        camp_location=request.form.get('camp_location') if request.form.get('camp_location') else None,
        org_name=request.form.get('org_name') if request.form.get('org_name') else None,
        package=request.form.get('package') if request.form.get('package') else None,
        diagnostic_partner=request.form.get('diagnostic_partner') if request.form.get('diagnostic_partner') else None,
        is_active=True,
        created_by=current_user.id,
        updated_by=current_user.id
    )
    
    db.session.add(camp_default)
    db.session.commit()
    
    flash('Camp information predefined successfully! These values will now appear as defaults for all users.', 'success')
    return redirect(url_for('camps.add'))


@bp.route('/remove-predefine', methods=['POST'])
@login_required
@require_module_access('camps')
def remove_predefine():
    """Remove predefined camp information (Admin only)."""
    # Check if user is admin
    if current_user.role != UserRole.ADMIN:
        flash('Only administrators can remove predefined camp information.', 'danger')
        return redirect(url_for('camps.add'))
    
    # Clear all active defaults
    CampDefault.clear_all_defaults()
    
    flash('Predefined camp information removed successfully!', 'success')
    return redirect(url_for('camps.add'))
