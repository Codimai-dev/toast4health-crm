"""Bookings forms."""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, DecimalField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional

from app.models import Customer, Employee


class BookingForm(FlaskForm):
    """Form for adding/editing bookings."""

    booking_code = StringField('Booking Code', validators=[DataRequired()],
                              render_kw={'class': 'form-control', 'placeholder': 'Enter booking code'})
    customer_name = StringField('Customer Name', validators=[DataRequired()],
                               render_kw={'class': 'form-control', 'placeholder': 'Enter customer name'})
    customer_mob = StringField('Customer Mobile', validators=[DataRequired()],
                              render_kw={'class': 'form-control', 'placeholder': 'Enter customer mobile'})
    services = TextAreaField('Services', validators=[DataRequired()],
                           render_kw={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter services'})
    start_date = DateField('Start Date', validators=[DataRequired()],
                          render_kw={'class': 'form-control'})
    end_date = DateField('End Date', render_kw={'class': 'form-control'})
    service_charge = DecimalField('Service Charge', validators=[DataRequired()],
                                render_kw={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'})
    other_expanse = DecimalField('Other Expenses', validators=[Optional()],
                               render_kw={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'})
    gst_percentage = IntegerField('GST Percentage', validators=[Optional()],
                                render_kw={'class': 'form-control', 'placeholder': '0'})
    amount_paid = DecimalField('Amount Paid', validators=[Optional()],
                             render_kw={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'})
    submit = SubmitField('Save Booking', render_kw={'class': 'btn btn-primary'})


class PaymentForm(FlaskForm):
    """Form for adding payments to bookings."""

    payment_amount = DecimalField('Payment Amount', validators=[DataRequired()],
                                render_kw={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'})
    payment_date = DateField('Payment Date', validators=[DataRequired()],
                           render_kw={'class': 'form-control'})
    submit = SubmitField('Add Payment', render_kw={'class': 'btn btn-primary'})