"""Customers forms."""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Optional

from app.models import ChannelPartner


class CustomerForm(FlaskForm):
    """Form for adding/editing customers."""

    customer_code = StringField('Customer Code', validators=[DataRequired()],
                               render_kw={'class': 'form-control', 'readonly': True})
    customer_name = StringField('Customer Name', validators=[DataRequired()],
                               render_kw={'class': 'form-control', 'placeholder': 'Enter customer name'})
    contact_no = StringField('Contact Number', validators=[DataRequired()],
                           render_kw={'class': 'form-control', 'placeholder': 'Enter contact number'})
    email = StringField('Email', validators=[Optional(), Email()],
                       render_kw={'class': 'form-control', 'placeholder': 'Enter email (optional)'})
    services = TextAreaField('Services', render_kw={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter services (optional)'})
    submit = SubmitField('Save Customer', render_kw={'class': 'btn btn-primary'})