"""Bookings routes."""

import os
import json
from flask import render_template, flash, redirect, url_for, Response, current_app
from flask_login import login_required, current_user
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from io import BytesIO

from app import db, require_module_access
from app.bookings import bp
from app.bookings.forms import BookingForm, PaymentForm, PaymentAddForm, PaymentEditForm
from app.models import Booking, Payment


@bp.route('/')
@login_required
@require_module_access('bookings')
def index():
    """Display all bookings."""
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    return render_template('bookings/index.html', title='Bookings', bookings=bookings)


@bp.route('/add', methods=['GET', 'POST'])
@login_required
@require_module_access('bookings')
def add():
    """Add a new booking."""
    form = BookingForm()
    # Auto-generate booking code
    booking_code = Booking.generate_booking_code()

    # Populate customer choices
    from app.models import Customer, B2CLead, Service
    customers = Customer.query.order_by(Customer.customer_name).all()
    converted_b2c = B2CLead.query.filter_by(status='converted').order_by(B2CLead.customer_name).all()

    customer_choices = []
    customer_data = {}
    for cust in customers:
        key = f'customer:{cust.id}'
        customer_choices.append((key, f'{cust.customer_name} ({cust.customer_code})'))
        customer_data[key] = {
            'mobile': cust.contact_no,
            'services': cust.services or ''
        }
    for b2c in converted_b2c:
        key = f'b2c:{b2c.enquiry_id}'
        customer_choices.append((key, f'{b2c.customer_name} ({b2c.enquiry_id})'))
        customer_data[key] = {
            'mobile': b2c.contact_no,
            'services': b2c.services or ''
        }

    form.customer_name.choices = [('', 'Select Customer')] + customer_choices
    
    # Populate service choices
    services = Service.query.order_by(Service.name).all()
    service_choices = [('', 'Select Service')] + [(s.name, s.name) for s in services]
    form.services.choices = service_choices

    customer_data_json = json.dumps(customer_data)

    if form.validate_on_submit():
        # Parse selected customer
        selected_customer = form.customer_name.data
        customer_type, customer_id = selected_customer.split(':', 1)
        customer_name = None
        customer_mob = None
        customer_id_fk = None

        if customer_type == 'customer':
            customer = Customer.query.get(int(customer_id))
            if customer:
                customer_name = customer.customer_name
                customer_mob = customer.contact_no
                customer_id_fk = customer.id
        elif customer_type == 'b2c':
            b2c_lead = B2CLead.query.filter_by(enquiry_id=customer_id).first()
            if b2c_lead:
                customer_name = b2c_lead.customer_name
                customer_mob = b2c_lead.contact_no

        # Custom validation for recurring charge
        if form.charge_type.data == 'Recurring charge':
            if not form.start_date.data:
                form.start_date.errors.append('Start Date is required for recurring charge.')
                return render_template('bookings/add.html', title='Add Booking', form=form)
            if not form.end_date.data:
                form.end_date.errors.append('End Date is required for recurring charge.')
                return render_template('bookings/add.html', title='Add Booking', form=form)
            if not form.shift.data:
                form.shift.errors.append('Shift is required for recurring charge.')
                return render_template('bookings/add.html', title='Add Booking', form=form)

        from datetime import datetime
        start_date = None
        end_date = None
        if form.start_date.data:
            start_date = datetime.strptime(form.start_date.data, '%Y-%m-%d').date()
        if form.end_date.data:
            end_date = datetime.strptime(form.end_date.data, '%Y-%m-%d').date()

        booking = Booking(
            booking_code=form.booking_code.data,
            customer_id=customer_id_fk,
            customer_name=customer_name,
            customer_mob=customer_mob,
            charge_type=form.charge_type.data,
            services=form.services.data,
            start_date=start_date,
            end_date=end_date,
            shift_hours=form.shift.data,
            service_charge=form.service_charge.data,
            other_expanse=form.other_expanse.data or 0,
            gst_percentage=form.gst_percentage.data or 0,
            amount_paid=form.amount_paid.data or 0,
            created_by=current_user.id,
            updated_by=current_user.id
        )
        booking.calculate_totals()
        db.session.add(booking)
        db.session.commit()

        # Create payment record if amount_paid > 0
        if form.amount_paid.data and form.amount_paid.data > 0:
            from datetime import date
            payment = Payment(
                booking_id=booking.id,
                payment_amount=form.amount_paid.data,
                payment_date=date.today(),
                payment_method=None,  # Blank payment method
                notes='Initial payment made during booking creation',
                created_by=current_user.id,
                updated_by=current_user.id
            )
            db.session.add(payment)
            db.session.commit()

        flash('Booking added successfully!', 'success')
        return redirect(url_for('bookings.index'))
    return render_template('bookings/add.html', title='Add Booking', form=form, booking_code=booking_code, customer_data_json=customer_data_json)


@bp.route('/view/<booking_code>')
@login_required
@require_module_access('bookings')
def view(booking_code):
    """View a booking."""
    booking = Booking.query.filter_by(booking_code=booking_code).first_or_404()
    payments = Payment.query.filter_by(booking_id=booking.id).order_by(Payment.payment_date.desc()).all()
    return render_template('bookings/view.html', title='View Booking', booking=booking, payments=payments)


@bp.route('/edit/<booking_code>', methods=['GET', 'POST'])
@login_required
@require_module_access('bookings')
def edit(booking_code):
    """Edit a booking."""
    booking = Booking.query.filter_by(booking_code=booking_code).first_or_404()
    form = BookingForm(obj=booking)

    # Populate customer choices
    from app.models import Customer, B2CLead, Service
    customers = Customer.query.order_by(Customer.customer_name).all()
    converted_b2c = B2CLead.query.filter_by(status='converted').order_by(B2CLead.customer_name).all()

    customer_choices = []
    customer_data = {}
    for cust in customers:
        key = f'customer:{cust.id}'
        customer_choices.append((key, f'{cust.customer_name} ({cust.customer_code})'))
        customer_data[key] = {
            'mobile': cust.contact_no,
            'services': cust.services or ''
        }
    for b2c in converted_b2c:
        key = f'b2c:{b2c.enquiry_id}'
        customer_choices.append((key, f'{b2c.customer_name} ({b2c.enquiry_id})'))
        customer_data[key] = {
            'mobile': b2c.contact_no,
            'services': b2c.services or ''
        }

    form.customer_name.choices = [('', 'Select Customer')] + customer_choices
    
    # Populate service choices
    services = Service.query.order_by(Service.name).all()
    service_choices = [('', 'Select Service')] + [(s.name, s.name) for s in services]
    form.services.choices = service_choices

    customer_data_json = json.dumps(customer_data)

    # Set initial customer selection
    if booking.customer_id:
        form.customer_name.data = f'customer:{booking.customer_id}'
        customer_info = customer_data.get(f'customer:{booking.customer_id}', {})
        form.customer_mob.data = customer_info.get('mobile', booking.customer_mob) if isinstance(customer_info, dict) else booking.customer_mob
    else:
        # Try to find matching B2C lead
        b2c_match = B2CLead.query.filter_by(customer_name=booking.customer_name, contact_no=booking.customer_mob, status='converted').first()
        if b2c_match:
            form.customer_name.data = f'b2c:{b2c_match.enquiry_id}'
            customer_info = customer_data.get(f'b2c:{b2c_match.enquiry_id}', {})
            form.customer_mob.data = customer_info.get('mobile', booking.customer_mob) if isinstance(customer_info, dict) else booking.customer_mob

    # Set date fields as strings for the form
    if booking.start_date:
        form.start_date.data = booking.start_date.strftime('%Y-%m-%d')
    if booking.end_date:
        form.end_date.data = booking.end_date.strftime('%Y-%m-%d')
    # Set shift field
    if booking.shift_hours:
        form.shift.data = booking.shift_hours

    if form.validate_on_submit():
        # Parse selected customer
        selected_customer = form.customer_name.data
        customer_type, customer_id = selected_customer.split(':', 1)
        customer_name = None
        customer_mob = None
        customer_id_fk = None

        if customer_type == 'customer':
            customer = Customer.query.get(int(customer_id))
            if customer:
                customer_name = customer.customer_name
                customer_mob = customer.contact_no
                customer_id_fk = customer.id
        elif customer_type == 'b2c':
            b2c_lead = B2CLead.query.filter_by(enquiry_id=customer_id).first()
            if b2c_lead:
                customer_name = b2c_lead.customer_name
                customer_mob = b2c_lead.contact_no

        # Custom validation for recurring charge
        if form.charge_type.data == 'Recurring charge':
            if not form.start_date.data:
                form.start_date.errors.append('Start Date is required for recurring charge.')
                return render_template('bookings/edit.html', title='Edit Booking', form=form, booking=booking)
            if not form.end_date.data:
                form.end_date.errors.append('End Date is required for recurring charge.')
                return render_template('bookings/edit.html', title='Edit Booking', form=form, booking=booking)
            if not form.shift.data:
                form.shift.errors.append('Shift is required for recurring charge.')
                return render_template('bookings/edit.html', title='Edit Booking', form=form, booking=booking)

        from datetime import datetime
        start_date = None
        end_date = None
        if form.start_date.data:
            start_date = datetime.strptime(form.start_date.data, '%Y-%m-%d').date()
        if form.end_date.data:
            end_date = datetime.strptime(form.end_date.data, '%Y-%m-%d').date()

        form.populate_obj(booking)
        booking.customer_id = customer_id_fk
        booking.customer_name = customer_name
        booking.customer_mob = customer_mob
        booking.start_date = start_date
        booking.end_date = end_date
        booking.charge_type = form.charge_type.data
        booking.shift_hours = form.shift.data
        booking.updated_by = current_user.id
        booking.calculate_totals()
        db.session.commit()
        flash('Booking updated successfully!', 'success')
        return redirect(url_for('bookings.index'))
    return render_template('bookings/edit.html', title='Edit Booking', form=form, booking=booking, customer_data_json=customer_data_json)


@bp.route('/payment/<booking_code>', methods=['GET', 'POST'])
@login_required
@require_module_access('bookings')
def payment(booking_code):
    """Add payment for a booking."""
    booking = Booking.query.filter_by(booking_code=booking_code).first_or_404()
    from app.bookings.forms import PaymentForm
    form = PaymentForm()
    if form.validate_on_submit():
        # Create payment record
        payment = Payment(
            booking_id=booking.id,
            payment_amount=form.payment_amount.data,
            payment_date=form.payment_date.data,
            payment_method=form.payment_method.data,
            notes=form.notes.data,
            created_by=current_user.id,
            updated_by=current_user.id
        )
        db.session.add(payment)

        # Update booking totals
        booking.amount_paid = (booking.amount_paid or 0) + form.payment_amount.data
        booking.last_payment_date = form.payment_date.data
        booking.calculate_totals()
        booking.updated_by = current_user.id
        db.session.commit()
        flash('Payment added successfully!', 'success')
        return redirect(url_for('bookings.view', booking_code=booking.booking_code))
    return render_template('bookings/payment.html', title='Add Payment', form=form, booking=booking)


@bp.route('/payments')
@login_required
@require_module_access('bookings')
def payments():
    """Display all payments."""
    payments = Payment.query.join(Booking).order_by(Payment.payment_date.desc()).all()
    return render_template('bookings/payments/index.html', title='Payments', payments=payments)


@bp.route('/payments/add', methods=['GET', 'POST'])
@login_required
@require_module_access('bookings')
def add_payment():
    """Add a new payment."""
    # Get all bookings for the dropdown
    bookings = Booking.query.order_by(Booking.booking_code).all()
    booking_choices = [(str(b.id), f"{b.booking_code} - {b.customer_name}") for b in bookings]

    form = PaymentAddForm()
    form.booking_id.choices = booking_choices

    if form.validate_on_submit():
        booking = Booking.query.get(int(form.booking_id.data))
        if not booking:
            flash('Invalid booking selected.', 'error')
            return render_template('bookings/payments/add.html', title='Add Payment', form=form)

        # Create payment record
        payment = Payment(
            booking_id=booking.id,
            payment_amount=form.payment_amount.data,
            payment_date=form.payment_date.data,
            payment_method=form.payment_method.data,
            notes=form.notes.data,
            created_by=current_user.id,
            updated_by=current_user.id
        )
        db.session.add(payment)

        # Update booking totals
        booking.amount_paid = (booking.amount_paid or 0) + form.payment_amount.data
        booking.last_payment_date = form.payment_date.data
        booking.calculate_totals()
        booking.updated_by = current_user.id
        db.session.commit()
        flash('Payment added successfully!', 'success')
        return redirect(url_for('bookings.payments'))

    return render_template('bookings/payments/add.html', title='Add Payment', form=form)


@bp.route('/payments/edit/<int:payment_id>', methods=['GET', 'POST'])
@login_required
@require_module_access('bookings')
def edit_payment(payment_id):
    """Edit an existing payment."""
    payment = Payment.query.get_or_404(payment_id)

    # Get all bookings for the dropdown
    bookings = Booking.query.order_by(Booking.booking_code).all()
    booking_choices = [(str(b.id), f"{b.booking_code} - {b.customer_name}") for b in bookings]

    form = PaymentEditForm(obj=payment)
    form.booking_id.choices = booking_choices

    if form.validate_on_submit():
        old_amount = payment.payment_amount
        old_booking_id = payment.booking_id

        booking = Booking.query.get(int(form.booking_id.data))
        if not booking:
            flash('Invalid booking selected.', 'error')
            return render_template('bookings/payments/edit.html', title='Edit Payment', form=form, payment=payment)

        # Update payment record
        payment.booking_id = booking.id
        payment.payment_amount = form.payment_amount.data
        payment.payment_date = form.payment_date.data
        payment.payment_method = form.payment_method.data
        payment.notes = form.notes.data
        payment.updated_by = current_user.id

        # Update booking totals
        if old_booking_id == booking.id:
            # Same booking, just adjust the amount
            amount_diff = payment.payment_amount - old_amount
            booking.amount_paid = (booking.amount_paid or 0) + amount_diff
        else:
            # Different booking - revert from old booking and add to new booking
            old_booking = Booking.query.get(old_booking_id)
            if old_booking:
                old_booking.amount_paid = (old_booking.amount_paid or 0) - old_amount
                old_booking.calculate_totals()
                old_booking.updated_by = current_user.id

            booking.amount_paid = (booking.amount_paid or 0) + payment.payment_amount

        booking.last_payment_date = form.payment_date.data
        booking.calculate_totals()
        booking.updated_by = current_user.id

        db.session.commit()
        flash('Payment updated successfully!', 'success')
        return redirect(url_for('bookings.payments'))

    return render_template('bookings/payments/edit.html', title='Edit Payment', form=form, payment=payment)


@bp.route('/invoice/<booking_code>')
@login_required
@require_module_access('bookings')
def invoice(booking_code):
    """Generate PDF invoice for a booking."""
    booking = Booking.query.filter_by(booking_code=booking_code).first_or_404()

    # Create PDF buffer
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1  # Center
    )

    normal_style = styles['Normal']
    heading_style = styles['Heading2']

    # Build PDF content
    content = []

    # Header
    content.append(Paragraph("Your Company Name", title_style))
    content.append(Paragraph("123 Business Street, City, State 12345", normal_style))
    content.append(Paragraph("Phone: (123) 456-7890 | Email: info@company.com", normal_style))
    content.append(Spacer(1, 20))
    content.append(Paragraph("INVOICE", title_style))

    # Invoice details
    invoice_data = [
        ['Invoice Number:', booking.booking_code, 'Invoice Date:', booking.created_at.strftime('%d-%m-%Y') if booking.created_at else ''],
        ['Bill To:', booking.customer_name, 'Service Period:', f"{booking.start_date.strftime('%d-%m-%Y') if booking.start_date else ''} - {booking.end_date.strftime('%d-%m-%Y') if booking.end_date else ''}"],
        ['', booking.customer_mob, '', '']
    ]

    if booking.customer and booking.customer.email:
        invoice_data.append(['', booking.customer.email, '', ''])

    invoice_table = Table(invoice_data, colWidths=[100, 150, 100, 150])
    invoice_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
    ]))
    content.append(invoice_table)
    content.append(Spacer(1, 20))

    # Services table
    content.append(Paragraph("Services", heading_style))
    services_data = [
        ['Description', 'Quantity', 'Unit Price', 'Amount'],
        [booking.services or '', '1', f"₹{booking.service_charge or 0:.2f}", f"₹{booking.service_charge or 0:.2f}"]
    ]

    if booking.other_expanse:
        services_data.append(['Other Expenses', '1', f"₹{booking.other_expanse:.2f}", f"₹{booking.other_expanse:.2f}"])

    services_table = Table(services_data, colWidths=[200, 80, 100, 100])
    services_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (0, 0), colors.lightgrey),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
    ]))
    content.append(services_table)
    content.append(Spacer(1, 20))

    # Totals
    subtotal = (booking.service_charge or 0) + (booking.other_expanse or 0)
    content.append(Paragraph(f"Subtotal: ₹{subtotal:.2f}", normal_style))

    if booking.gst_percentage:
        content.append(Paragraph(f"GST ({booking.gst_percentage}%): ₹{booking.gst_value or 0:.2f}", normal_style))

    content.append(Paragraph(f"<b>Total Amount: ₹{booking.total_amount or 0:.2f}</b>", normal_style))
    content.append(Paragraph(f"Amount Paid: ₹{booking.amount_paid or 0:.2f}", normal_style))
    content.append(Paragraph(f"Balance Due: ₹{booking.pending_amount or 0:.2f}", normal_style))

    # Footer
    content.append(Spacer(1, 30))
    content.append(Paragraph("Thank you for your business!", normal_style))
    content.append(Paragraph("Payment terms: Due upon receipt", normal_style))
    content.append(Paragraph("For any queries, please contact us at info@company.com", normal_style))

    # Generate PDF
    doc.build(content)
    buffer.seek(0)

    # Return PDF response
    response = Response(buffer.getvalue(), mimetype='application/pdf')
    response.headers['Content-Disposition'] = f'attachment; filename=invoice_{booking.booking_code}.pdf'
    return response