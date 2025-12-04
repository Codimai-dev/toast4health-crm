"""B2C Leads routes."""

import csv
from datetime import datetime, date
from io import StringIO
from flask import render_template, flash, redirect, url_for, request, Response
from flask_login import login_required, current_user

from app import db, require_module_access
from app.leads_b2c import bp
from app.leads_b2c.forms import B2CLeadForm, CSVImportForm
from app.models import B2CLead, ChannelPartner, Service, FollowUp, FollowUpOutcome, LeadType


@bp.route('/')
@login_required
@require_module_access('leads_b2c')
def index():
    """Display all B2C leads."""
    leads = B2CLead.query.order_by(B2CLead.created_at.desc()).all()
    return render_template('leads_b2c/index.html', title='B2C Leads', leads=leads)


@bp.route('/export')
@login_required
@require_module_access('leads_b2c')
def export():
    """Export B2C leads to CSV."""
    leads = B2CLead.query.order_by(B2CLead.created_at.desc()).all()

    # Create CSV in memory
    output = StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        'Enquiry ID', 'Customer Name', 'Contact No', 'Email', 'Enquiry Date',
        'Source', 'Services', 'Referred By', 'Status', 'Comment',
        'Followup 1', 'Followup 1 Detail', 'Followup 2', 'Followup 2 Detail',
        'Followup 3', 'Followup 3 Detail', 'Customer ID'
    ])

    # Write data
    for lead in leads:
        writer.writerow([
            lead.enquiry_id,
            lead.customer_name,
            lead.contact_no,
            lead.email,
            lead.enquiry_date.strftime('%d-%m-%Y') if lead.enquiry_date else '',
            lead.source if lead.source else '',
            lead.services,
            lead.referred_by,
            lead.status,
            lead.comment,
            lead.followup1.strftime('%d-%m-%Y') if lead.followup1 else '',
            lead.followup1_detail,
            lead.followup2.strftime('%d-%m-%Y') if lead.followup2 else '',
            lead.followup2_detail,
            lead.followup3.strftime('%d-%m-%Y') if lead.followup3 else '',
            lead.followup3_detail,
            lead.customer_id
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=b2c_leads.csv'}
    )


def parse_date(date_str):
    """Parse date string with multiple format support."""
    formats = [
        '%Y-%m-%d',  # 2023-12-25
        '%d/%m/%Y',  # 25/12/2023
        '%m/%d/%Y',  # 12/25/2023
        '%d-%m-%Y',  # 25-12-2023
        '%m-%d-%Y',  # 12-25-2023
        '%Y/%m/%d',  # 2023/12/25
        '%d.%m.%Y',  # 25.12.2023
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None


@bp.route('/import', methods=['GET', 'POST'])
@login_required
@require_module_access('leads_b2c')
def import_csv():
    """Import B2C leads from CSV."""
    form = CSVImportForm()
    import_results = None

    if form.validate_on_submit():
        csv_file = form.csv_file.data
        csv_content = csv_file.read().decode('utf-8')
        csv_reader = csv.DictReader(StringIO(csv_content))

        success_count = 0
        error_count = 0
        errors = []

        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 because row 1 is header
            try:
                # Check if enquiry_id already exists
                enquiry_id = row.get('Enquiry ID', '').strip()
                if not enquiry_id:
                    errors.append(f"Row {row_num}: Enquiry ID is required")
                    error_count += 1
                    continue

                existing_lead = B2CLead.query.filter_by(enquiry_id=enquiry_id).first()
                if existing_lead:
                    errors.append(f"Row {row_num}: Enquiry ID '{enquiry_id}' already exists")
                    error_count += 1
                    continue

                # Parse enquiry_date
                enquiry_date_str = row.get('Enquiry Date', '').strip()
                enquiry_date = None
                if enquiry_date_str:
                    enquiry_date = parse_date(enquiry_date_str)
                    if not enquiry_date:
                        errors.append(f"Row {row_num}: Invalid enquiry date format (supported: DD/MM/YYYY, MM/DD/YYYY, YYYY-MM-DD, DD-MM-YYYY)")
                        error_count += 1
                        continue

                # Parse followup dates
                followup1 = None
                followup1_str = row.get('Followup 1', '').strip()
                if followup1_str:
                    followup1 = parse_date(followup1_str)

                followup2 = None
                followup2_str = row.get('Followup 2', '').strip()
                if followup2_str:
                    followup2 = parse_date(followup2_str)

                followup3 = None
                followup3_str = row.get('Followup 3', '').strip()
                if followup3_str:
                    followup3 = parse_date(followup3_str)

                # Create lead
                lead = B2CLead(
                    enquiry_id=enquiry_id,
                    customer_name=row.get('Customer Name', '').strip(),
                    contact_no=row.get('Contact No', '').strip(),
                    email=row.get('Email', '').strip() or None,
                    enquiry_date=enquiry_date,
                    source=row.get('Source', '').strip() or None,
                    services=row.get('Services', '').strip() or None,
                    referred_by=row.get('Referred By', '').strip() or None,
                    status=row.get('Status', 'NEW').strip(),
                    comment=row.get('Comment', '').strip() or None,
                    followup1=followup1,
                    followup1_detail=row.get('Followup 1 Detail', '').strip() or None,
                    followup2=followup2,
                    followup2_detail=row.get('Followup 2 Detail', '').strip() or None,
                    followup3=followup3,
                    followup3_detail=row.get('Followup 3 Detail', '').strip() or None,
                    customer_id=row.get('Customer ID', '').strip() or None,
                    created_by=current_user.id,
                    updated_by=current_user.id
                )

                db.session.add(lead)
                success_count += 1

            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
                error_count += 1

        db.session.commit()
        import_results = {
            'success_count': success_count,
            'error_count': error_count,
            'errors': errors[:10]  # Show first 10 errors
        }

        flash(f'Import completed: {success_count} leads imported, {error_count} errors', 'info')

    return render_template('leads_b2c/import.html', title='Import B2C Leads', form=form, import_results=import_results)


@bp.route('/add', methods=['GET', 'POST'])
@login_required
@require_module_access('leads_b2c')
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

        # Create automatic follow-up for the new B2C lead
        followup = FollowUp(
            lead_type=LeadType.B2C,
            b2c_lead_id=lead.enquiry_id,
            follow_up_on=date.today(),
            outcome=FollowUpOutcome.SCHEDULED,
            notes='Automatic follow-up created for new B2C lead',
            next_follow_up_on=None,
            owner_id=current_user.id
        )
        db.session.add(followup)
        db.session.commit()

        flash('B2C lead added successfully!', 'success')
        return redirect(url_for('leads_b2c.index'))
    return render_template('leads_b2c/add.html', title='Add B2C Lead', form=form)


@bp.route('/view/<enquiry_id>')
@login_required
@require_module_access('leads_b2c')
def view(enquiry_id):
    """View a B2C lead."""
    lead = B2CLead.query.filter_by(enquiry_id=enquiry_id).first_or_404()
    return render_template('leads_b2c/view.html', title='View B2C Lead', lead=lead)


@bp.route('/edit/<enquiry_id>', methods=['GET', 'POST'])
@login_required
@require_module_access('leads_b2c')
def edit(enquiry_id):
    """Edit a B2C lead."""
    lead = B2CLead.query.filter_by(enquiry_id=enquiry_id).first_or_404()
    form = B2CLeadForm(obj=lead)
    form.referred_by.choices = [('', 'Select Channel Partner')] + [(cp.name, cp.name) for cp in ChannelPartner.query.order_by(ChannelPartner.name).all()]

    # Set the correct service selection based on stored service name
    if lead.services:
        service = Service.query.filter_by(name=lead.services).first()
        if service:
            form.services.data = str(service.id)

    # Set the correct source and status selection only for GET requests
    from flask import request
    if request.method == 'GET':
        form.source.data = lead.source
        form.status.data = lead.status

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
@require_module_access('leads_b2c')
def follow_up(enquiry_id):
    """Add follow-up for a B2C lead."""
    lead = B2CLead.query.filter_by(enquiry_id=enquiry_id).first_or_404()
    from app.leads_b2c.forms import FollowUpForm
    form = FollowUpForm()
    if form.validate_on_submit():
        from app.models import FollowUp, FollowUpOutcome
        followup = FollowUp(
            lead_type='B2C',
            b2c_lead_id=lead.enquiry_id,
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