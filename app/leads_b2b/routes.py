"""B2B Leads routes."""

from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user

from app import db, require_module_access
from app.leads_b2b import bp
from app.leads_b2b.forms import B2BLeadForm
from app.models import B2BLead


@bp.route('/')
@login_required
@require_module_access('leads_b2b')
def index():
    """Display all B2B leads."""
    leads = B2BLead.query.order_by(B2BLead.created_at.desc()).all()
    return render_template('leads_b2b/index.html', title='B2B Leads', leads=leads)


@bp.route('/add', methods=['GET', 'POST'])
@login_required
@require_module_access('leads_b2b')
def add():
    """Add a new B2B lead."""
    form = B2BLeadForm()
    generated_sr_no = B2BLead.generate_sr_no()
    form.sr_no.data = generated_sr_no
    if form.validate_on_submit():
        lead = B2BLead(
            sr_no=generated_sr_no,
            t4h_spoc=form.t4h_spoc.data,
            date=form.date.data,
            organization_name=form.organization_name.data,
            organization_email=form.organization_email.data,
            location=form.location.data,
            type_of_leads=form.type_of_leads.data,
            org_poc_name_and_role=form.org_poc_name_and_role.data,
            employee_size=form.employee_size.data,
            employee_wellness_program=form.employee_wellness_program.data,
            budget_of_wellness_program=form.budget_of_wellness_program.data,
            last_wellness_activity_done=form.last_wellness_activity_done.data,
            email1=form.email1.data,
            email2=form.email2.data,
            email3=form.email3.data,
            email4=form.email4.data,
            email5=form.email5.data,
            meeting1=form.meeting1.data,
            meeting1_notes=form.meeting1_notes.data,
            meeting1_task_done=form.meeting1_task_done.data,
            meeting2=form.meeting2.data,
            notes=form.notes.data,
            task_done=form.task_done.data,
            status=form.status.data,
            created_by=current_user.id,
            updated_by=current_user.id
        )
        db.session.add(lead)
        db.session.commit()
        flash('B2B lead added successfully!', 'success')
        return redirect(url_for('leads_b2b.index'))
    return render_template('leads_b2b/add.html', title='Add B2B Lead', form=form)


@bp.route('/view/<sr_no>')
@login_required
@require_module_access('leads_b2b')
def view(sr_no):
    """View a B2B lead."""
    lead = B2BLead.query.filter_by(sr_no=sr_no).first_or_404()
    return render_template('leads_b2b/view.html', title='View B2B Lead', lead=lead)


@bp.route('/edit/<sr_no>', methods=['GET', 'POST'])
@login_required
@require_module_access('leads_b2b')
def edit(sr_no):
    """Edit a B2B lead."""
    lead = B2BLead.query.filter_by(sr_no=sr_no).first_or_404()
    form = B2BLeadForm(obj=lead)
    if form.validate_on_submit():
        form.populate_obj(lead)
        lead.updated_by = current_user.id
        db.session.commit()
        flash('B2B lead updated successfully!', 'success')
        return redirect(url_for('leads_b2b.index'))
    return render_template('leads_b2b/edit.html', title='Edit B2B Lead', form=form, lead=lead)


@bp.route('/follow_up/<sr_no>', methods=['GET', 'POST'])
@login_required
@require_module_access('leads_b2b')
def follow_up(sr_no):
    """Add follow-up for a B2B lead."""
    lead = B2BLead.query.filter_by(sr_no=sr_no).first_or_404()
    from app.leads_b2c.forms import FollowUpForm
    form = FollowUpForm()
    if form.validate_on_submit():
        from app.models import FollowUp, FollowUpOutcome
        followup = FollowUp(
            lead_type='B2B',
            b2b_lead_id=lead.id,
            follow_up_on=form.follow_up_on.data,
            notes=form.notes.data,
            outcome=form.outcome.data,
            next_follow_up_on=form.next_follow_up_on.data,
            owner_id=current_user.id
        )
        db.session.add(followup)
        db.session.commit()
        flash('Follow-up added successfully!', 'success')
        return redirect(url_for('leads_b2b.view', sr_no=lead.sr_no))
    return render_template('leads_b2b/follow_up.html', title='Add Follow-up', form=form, lead=lead)