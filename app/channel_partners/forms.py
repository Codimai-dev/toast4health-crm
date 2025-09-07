"""Channel Partners forms."""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SubmitField
from wtforms.validators import DataRequired, Email, Optional, Length

from app.models import ChannelPartner


class ChannelPartnerForm(FlaskForm):
    """Form for adding/editing channel partners."""

    partner_code = StringField('Partner Code', validators=[DataRequired(), Length(max=20)],
                              render_kw={'class': 'form-control', 'placeholder': 'Enter partner code'})
    name = StringField('Partner Name', validators=[DataRequired(), Length(max=100)],
                      render_kw={'class': 'form-control', 'placeholder': 'Enter partner name'})
    contact_no = StringField('Contact Number', validators=[DataRequired(), Length(max=20)],
                            render_kw={'class': 'form-control', 'placeholder': 'Enter contact number'})
    email = StringField('Email', validators=[Optional(), Email(), Length(max=120)],
                       render_kw={'class': 'form-control', 'placeholder': 'Enter email (optional)'})
    created_date = DateField('Created Date', validators=[DataRequired()],
                            render_kw={'class': 'form-control', 'type': 'date'})
    notes = TextAreaField('Notes', validators=[Optional()],
                         render_kw={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter notes (optional)'})
    submit = SubmitField('Save Partner', render_kw={'class': 'btn btn-primary'})