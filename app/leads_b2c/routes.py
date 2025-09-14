"""B2C Leads routes."""

from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user

from app import db
from app.leads_b2c import bp
from app.leads_b2c.forms import B2CLeadForm
from app.models import B2CLead, ChannelPartner, Service


@bp.route('/')
@login_required
def index():
    """Display all B2C leads."""
    leads = B2CLead.query.order_by(B2CLead.created_at.desc()).all()
    return render_template('leads_b2c/index.html', title='B2C Leads', leads=leads)


@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add a new B2C lead."""
    form = B2CLeadForm()
    form.referred_by.choices = [('', 'Select Channel Partner')] + [(cp.name, cp.name) for cp in ChannelPartner.query.order_by(ChannelPartner.name).all()]
    # Auto-generate enquiry_id for new leads
    if not form.enquiry_id.data:
        form.enquiry_id.data = B2CLead.generate_enquiry_id()
    if form.validate_on_submit():
        # Convert service ID to service name
        service_name = None
        if form.services.data:
            service = Service.query.get(int(form.services.data))
            service_name = service.name if service else None

        lead = B2CLead(
            enquiry_id=form.enquiry_id.data,
            customer_name=form.customer_name.data,
            contact_no=form.contact_no.data,
            email=form.email.data,
            enquiry_date=form.enquiry_date.data,
            source=form.source.data if form.source.data else None,
            services=service_name,
            referred_by=form.referred_by.data if form.referred_by.data else None,
            status=form.status.data,
            comment=form.comment.data,
            created_by=current_user.id,
            updated_by=current_user.id
        )
        db.session.add(lead)
        db.session.commit()
        flash('B2C lead added successfully!', 'success')
        return redirect(url_for('leads_b2c.index'))
    return render_template('leads_b2c/add.html', title='Add B2C Lead', form=form)


@bp.route('/view/<enquiry_id>')
@login_required
def view(enquiry_id):
    """View a B2C lead."""
    lead = B2CLead.query.filter_by(enquiry_id=enquiry_id).first_or_404()
    return render_template('leads_b2c/view.html', title='View B2C Lead', lead=lead)


@bp.route('/edit/<enquiry_id>', methods=['GET', 'POST'])
@login_required
def edit(enquiry_id):
    """Edit a B2C lead."""
    lead = B2CLead.query.filter_by(enquiry_id=enquiry_id).first_or_404()
    form = B2CLeadForm(obj=lead)
    form.referred_by.choices = [('', 'Select Channel Partner')] + [(cp.name, cp.name) for cp in ChannelPartner.query.order_by(ChannelPartner.name).all()]

    # Set the correct source and status selection
    form.source.data = lead.source.value if lead.source else None
    form.status.data = lead.status.value

    # Set the correct service selection based on stored service name
    if lead.services:
        service = Service.query.filter_by(name=lead.services).first()
        if service:
            form.services.data = str(service.id)

    if form.validate_on_submit():
        # Convert service ID to service name
        service_name = None
        if form.services.data:
            service = Service.query.get(int(form.services.data))
            service_name = service.name if service else None

        form.populate_obj(lead)
        lead.source = form.source.data if form.source.data else None
        lead.services = service_name
        lead.referred_by = form.referred_by.data if form.referred_by.data else None
        lead.updated_by = current_user.id
        db.session.commit()
        flash('B2C lead updated successfully!', 'success')
        return redirect(url_for('leads_b2c.index'))
    return render_template('leads_b2c/edit.html', title='Edit B2C Lead', form=form, lead=lead)


@bp.route('/follow_up/<enquiry_id>', methods=['GET', 'POST'])
@login_required
def follow_up(enquiry_id):
    """Add follow-up for a B2C lead."""
    lead = B2CLead.query.filter_by(enquiry_id=enquiry_id).first_or_404()
    from app.leads_b2c.forms import FollowUpForm
    form = FollowUpForm()
    if form.validate_on_submit():
        from app.models import FollowUp, FollowUpOutcome
        followup = FollowUp(
            lead_type='B2C',
            b2c_lead_id=lead.id,
            follow_up_on=form.follow_up_on.data,
            notes=form.notes.data,
            outcome=form.outcome.data,
            next_follow_up_on=form.next_follow_up_on.data,
            owner_id=current_user.id
        )
        db.session.add(followup)
        db.session.commit()
        flash('Follow-up added successfully!', 'success')
        return redirect(url_for('leads_b2c.view', enquiry_id=lead.enquiry_id))
    return render_template('leads_b2c/follow_up.html', title='Add Follow-up', form=form, lead=lead)