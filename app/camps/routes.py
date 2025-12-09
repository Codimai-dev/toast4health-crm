"""Camp routes."""

from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user

from app import db, require_module_access
from app.camps import bp
from app.camps.forms import CampForm
from app.models import Camp


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
    generated_camp_id = Camp.generate_camp_id()
    form.camp_id.data = generated_camp_id
    
    if form.validate_on_submit():
        camp = Camp(
            camp_id=generated_camp_id,
            staff_id=int(form.staff_name.data) if form.staff_name.data else None,
            camp_date=form.camp_date.data,
            camp_location=form.camp_location.data,
            referred_by=form.referred_by.data,
            patient_name=form.patient_name.data,
            age=form.age.data,
            gender=form.gender.data if form.gender.data else None,
            test_done=form.test_done.data,
            package=form.package.data,
            diagnostic_partner=form.diagnostic_partner.data,
            phone_no=form.phone_no.data,
            payment=form.payment.data,
            created_by=current_user.id,
            updated_by=current_user.id
        )
        db.session.add(camp)
        db.session.commit()
        flash('Camp entry added successfully!', 'success')
        return redirect(url_for('camps.index'))
    
    return render_template('camps/add.html', title='Add Camp Entry', form=form)


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
        form.staff_name.data = str(camp.staff_id) if camp.staff_id else ''
        form.camp_date.data = camp.camp_date
        form.camp_location.data = camp.camp_location
        form.referred_by.data = camp.referred_by
        form.patient_name.data = camp.patient_name
        form.age.data = camp.age
        form.gender.data = camp.gender
        form.test_done.data = camp.test_done
        form.package.data = camp.package
        form.diagnostic_partner.data = camp.diagnostic_partner
        form.phone_no.data = camp.phone_no
        form.payment.data = camp.payment
    
    if form.validate_on_submit():
        camp.staff_id = int(form.staff_name.data) if form.staff_name.data else None
        camp.camp_date = form.camp_date.data
        camp.camp_location = form.camp_location.data
        camp.referred_by = form.referred_by.data
        camp.patient_name = form.patient_name.data
        camp.age = form.age.data
        camp.gender = form.gender.data if form.gender.data else None
        camp.test_done = form.test_done.data
        camp.package = form.package.data
        camp.diagnostic_partner = form.diagnostic_partner.data
        camp.phone_no = form.phone_no.data
        camp.payment = form.payment.data
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
