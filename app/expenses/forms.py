"""Expenses forms."""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional

from app.models import Booking


class ExpenseForm(FlaskForm):
    """Form for adding/editing expenses."""

    expense_code = StringField('Expense Code', validators=[],
                              render_kw={'class': 'form-control', 'disabled': True})
    date = DateField('Date', validators=[DataRequired()],
                    render_kw={'class': 'form-control', 'type': 'date'})
    category = StringField('Category', validators=[DataRequired()],
                          render_kw={'class': 'form-control', 'placeholder': 'Enter category'})
    sub_category = StringField('Sub Category', validators=[Optional()],
                              render_kw={'class': 'form-control', 'placeholder': 'Enter sub category'})
    expense_amount = DecimalField('Expense Amount', validators=[DataRequired(), NumberRange(min=0)],
                                 places=2, render_kw={'class': 'form-control', 'placeholder': 'Enter amount', 'step': '0.01'})
    booking_id = SelectField('Related Booking', choices=[('', 'Select Booking')], validators=[Optional()],
                            render_kw={'class': 'form-select'})
    other_id = StringField('Other ID', validators=[Optional()],
                          render_kw={'class': 'form-control', 'placeholder': 'Enter other ID'})
    submit = SubmitField('Save Expense', render_kw={'class': 'btn btn-primary'})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate booking choices
        from app.models import Booking
        bookings = Booking.query.all()
        self.booking_id.choices = [('', 'Select Booking')] + [(str(b.id), f"{b.booking_code} - {b.customer_name}") for b in bookings]