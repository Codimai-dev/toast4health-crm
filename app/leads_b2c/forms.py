"""B2C Leads forms."""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Optional

from app.models import LeadStatus, FollowUpOutcome, LeadSource


class B2CLeadForm(FlaskForm):
    """Form for adding/editing B2C leads."""

    enquiry_id = StringField('Enquiry ID', validators=[DataRequired()],
                           render_kw={'class': 'form-control', 'placeholder': 'Enter enquiry ID'})
    customer_name = StringField('Customer Name', validators=[DataRequired()],
                              render_kw={'class': 'form-control', 'placeholder': 'Enter customer name'})
    contact_no = StringField('Contact Number', validators=[DataRequired()],
                           render_kw={'class': 'form-control', 'placeholder': 'Enter contact number'})
    email = StringField('Email', validators=[Optional(), Email()],
                       render_kw={'class': 'form-control', 'placeholder': 'Enter email (optional)'})
    enquiry_date = DateField('Enquiry Date', validators=[DataRequired()],
                           render_kw={'class': 'form-control'})
    source = SelectField('Source', choices=[('', 'Select Source')] + [(source.value, source.value.replace('_', ' ')) for source in LeadSource],
                         render_kw={'class': 'form-select'})
    services = StringField('Services', render_kw={'class': 'form-control', 'placeholder': 'Enter services (optional)'})
    referred_by = StringField('Referred By', render_kw={'class': 'form-control', 'placeholder': 'Enter referrer (optional)'})
    status = SelectField('Status', choices=[(status.value, status.value.replace('_', ' ')) for status in LeadStatus],
                        default=LeadStatus.NEW.value, render_kw={'class': 'form-select'})
    comment = TextAreaField('Comment', render_kw={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter comment (optional)'})
    submit = SubmitField('Save Lead', render_kw={'class': 'btn btn-primary'})


class FollowUpForm(FlaskForm):
    """Form for adding follow-ups."""

    follow_up_on = DateField('Follow-up Date', validators=[DataRequired()],
                           render_kw={'class': 'form-control'})
    notes = TextAreaField('Notes', render_kw={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter follow-up notes'})
    outcome = SelectField('Outcome', choices=[(outcome.value, outcome.value.replace('_', ' ')) for outcome in FollowUpOutcome],
                        validators=[DataRequired()], render_kw={'class': 'form-select'})
    next_follow_up_on = DateField('Next Follow-up Date', validators=[Optional()],
                                render_kw={'class': 'form-control'})
    submit = SubmitField('Add Follow-up', render_kw={'class': 'btn btn-primary'})