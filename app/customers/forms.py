"""Customers forms."""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Optional

from app.models import ChannelPartner


class CustomerForm(FlaskForm):
    """Form for adding/editing customers."""

    customer_code = StringField('Customer Code', validators=[DataRequired()],
                               render_kw={'class': 'form-control', 'readonly': True, 'autocomplete': 'off'})
    customer_name = StringField('Customer Name', validators=[DataRequired()],
                               render_kw={'class': 'form-control', 'placeholder': 'Enter customer name', 'autocomplete': 'off'})
    contact_no = StringField('Contact Number', validators=[DataRequired()],
                           render_kw={'class': 'form-control', 'placeholder': 'Enter contact number', 'autocomplete': 'off'})
    email = StringField('Email', validators=[Optional(), Email()],
                       render_kw={'class': 'form-control', 'placeholder': 'Enter email (optional)', 'autocomplete': 'off'})
    services = SelectField('Services', choices=[], validators=[Optional()],
                          render_kw={'class': 'form-control', 'autocomplete': 'off'})
    submit = SubmitField('Save Customer', render_kw={'class': 'btn btn-primary'})