"""Bookings routes."""

from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user

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
    if form.validate_on_submit():
        booking = Booking(
            booking_code=form.booking_code.data,
            customer_name=form.customer_name.data,
            customer_mob=form.customer_mob.data,
            services=form.services.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
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
    return render_template('bookings/add.html', title='Add Booking', form=form)


@bp.route('/view/<int:id>')
@login_required
@require_module_access('bookings')
def view(id):
    """View a booking."""
    booking = Booking.query.get_or_404(id)
    return render_template('bookings/view.html', title='View Booking', booking=booking)


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@require_module_access('bookings')
def edit(id):
    """Edit a booking."""
    booking = Booking.query.get_or_404(id)
    form = BookingForm(obj=booking)
    if form.validate_on_submit():
        form.populate_obj(booking)
        booking.updated_by = current_user.id
        booking.calculate_totals()
        db.session.commit()
        flash('Booking updated successfully!', 'success')
        return redirect(url_for('bookings.index'))
    return render_template('bookings/edit.html', title='Edit Booking', form=form, booking=booking)


@bp.route('/payment/<int:id>', methods=['GET', 'POST'])
@login_required
@require_module_access('bookings')
def payment(id):
    """Add payment for a booking."""
    booking = Booking.query.get_or_404(id)
    from app.bookings.forms import PaymentForm
    form = PaymentForm()
    if form.validate_on_submit():
        booking.amount_paid = (booking.amount_paid or 0) + form.payment_amount.data
        booking.last_payment_date = form.payment_date.data
        booking.calculate_totals()
        booking.updated_by = current_user.id
        db.session.commit()
        flash('Payment added successfully!', 'success')
        return redirect(url_for('bookings.view', id=booking.id))
    return render_template('bookings/payment.html', title='Add Payment', form=form, booking=booking)