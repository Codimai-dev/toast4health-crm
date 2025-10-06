"""Bookings routes."""

import os
from flask import render_template, flash, redirect, url_for, Response, current_app
from flask_login import login_required, current_user
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from io import BytesIO

from app import db, require_module_access
from app.bookings import bp
from app.bookings.forms import BookingForm
from app.models import Booking


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
    if form.validate_on_submit():
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
            customer_name=form.customer_name.data,
            customer_mob=form.customer_mob.data,
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
        flash('Booking added successfully!', 'success')
        return redirect(url_for('bookings.index'))
    return render_template('bookings/add.html', title='Add Booking', form=form, booking_code=booking_code)


@bp.route('/view/<booking_code>')
@login_required
@require_module_access('bookings')
def view(booking_code):
    """View a booking."""
    booking = Booking.query.filter_by(booking_code=booking_code).first_or_404()
    return render_template('bookings/view.html', title='View Booking', booking=booking)


@bp.route('/edit/<booking_code>', methods=['GET', 'POST'])
@login_required
@require_module_access('bookings')
def edit(booking_code):
    """Edit a booking."""
    booking = Booking.query.filter_by(booking_code=booking_code).first_or_404()
    form = BookingForm(obj=booking)
    # Set date fields as strings for the form
    if booking.start_date:
        form.start_date.data = booking.start_date.strftime('%Y-%m-%d')
    if booking.end_date:
        form.end_date.data = booking.end_date.strftime('%Y-%m-%d')
    # Set shift field
    if booking.shift_hours:
        form.shift.data = booking.shift_hours

    if form.validate_on_submit():
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
        booking.start_date = start_date
        booking.end_date = end_date
        booking.charge_type = form.charge_type.data
        booking.shift_hours = form.shift.data
        booking.updated_by = current_user.id
        booking.calculate_totals()
        db.session.commit()
        flash('Booking updated successfully!', 'success')
        return redirect(url_for('bookings.index'))
    return render_template('bookings/edit.html', title='Edit Booking', form=form, booking=booking)


@bp.route('/payment/<booking_code>', methods=['GET', 'POST'])
@login_required
@require_module_access('bookings')
def payment(booking_code):
    """Add payment for a booking."""
    booking = Booking.query.filter_by(booking_code=booking_code).first_or_404()
    from app.bookings.forms import PaymentForm
    form = PaymentForm()
    if form.validate_on_submit():
        booking.amount_paid = (booking.amount_paid or 0) + form.payment_amount.data
        booking.last_payment_date = form.payment_date.data
        booking.calculate_totals()
        booking.updated_by = current_user.id
        db.session.commit()
        flash('Payment added successfully!', 'success')
        return redirect(url_for('bookings.view', booking_code=booking.booking_code))
    return render_template('bookings/payment.html', title='Add Payment', form=form, booking=booking)


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
        ['Invoice Number:', booking.booking_code, 'Invoice Date:', booking.created_at.strftime('%d/%m/%Y') if booking.created_at else ''],
        ['Bill To:', booking.customer_name, 'Service Period:', f"{booking.start_date.strftime('%d/%m/%Y') if booking.start_date else ''} - {booking.end_date.strftime('%d/%m/%Y') if booking.end_date else ''}"],
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