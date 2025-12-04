"""B2C Leads forms."""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, TextAreaField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Optional

from app.models import FollowUpOutcome, Service, Setting


class B2CLeadForm(FlaskForm):
    """Form for adding/editing B2C leads."""

    enquiry_id = StringField('Enquiry ID', validators=[DataRequired()],
                           render_kw={'class': 'form-control', 'readonly': True, 'autocomplete': 'off'})
    customer_name = StringField('Customer Name', validators=[DataRequired()],
                              render_kw={'class': 'form-control', 'placeholder': 'Enter customer name', 'autocomplete': 'off'})
    contact_no = StringField('Contact Number', validators=[DataRequired()],
                           render_kw={'class': 'form-control', 'placeholder': 'Enter contact number', 'autocomplete': 'off'})
    email = StringField('Email', validators=[Optional(), Email()],
                       render_kw={'class': 'form-control', 'placeholder': 'Enter email (optional)', 'autocomplete': 'off'})
    enquiry_date = DateField('Enquiry Date', validators=[DataRequired()],
                           render_kw={'class': 'form-control', 'autocomplete': 'off'})
    source = SelectField('Source', choices=[], render_kw={'class': 'form-select', 'autocomplete': 'off'})
    services = SelectField('Services', choices=[], render_kw={'class': 'form-select', 'autocomplete': 'off'})
    referred_by = SelectField('Referred By', choices=[], render_kw={'class': 'form-select', 'autocomplete': 'off'})
    status = SelectField('Status', choices=[], default='NEW', render_kw={'class': 'form-select', 'autocomplete': 'off'})
    comment = TextAreaField('Comment', render_kw={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter comment (optional)', 'autocomplete': 'off'})
    submit = SubmitField('Save Lead', render_kw={'class': 'btn btn-primary'})

    def __init__(self, *args, **kwargs):
        super(B2CLeadForm, self).__init__(*args, **kwargs)
        # Populate choices from settings
        self.source.choices = [('', 'Select Source')] + [(setting.key, setting.value) for setting in Setting.get_options('Source')]
        self.status.choices = [(setting.key, setting.value) for setting in Setting.get_options('LeadStatus')]
        # Populate services choices from database
        self.services.choices = [('', 'Select Service')] + [(str(service.id), service.name) for service in Service.query.order_by(Service.name).all()]


class FollowUpForm(FlaskForm):
    """Form for adding follow-ups."""

    follow_up_on = DateField('Follow-up Date', validators=[DataRequired()],
                           render_kw={'class': 'form-control', 'autocomplete': 'off'})
    notes = TextAreaField('Notes', render_kw={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter follow-up notes', 'autocomplete': 'off'})
    outcome = SelectField('Outcome', choices=[(outcome.value, outcome.value.replace('_', ' ')) for outcome in FollowUpOutcome],
                        validators=[DataRequired()], render_kw={'class': 'form-select', 'autocomplete': 'off'})
    next_follow_up_on = DateField('Next Follow-up Date', validators=[Optional()],
                                render_kw={'class': 'form-control', 'autocomplete': 'off'})
    submit = SubmitField('Add Follow-up', render_kw={'class': 'btn btn-primary'})


class CSVImportForm(FlaskForm):
    """Form for importing B2C leads from CSV."""

    csv_file = FileField('CSV File', validators=[FileRequired()],
                        render_kw={'class': 'form-control', 'accept': '.csv', 'autocomplete': 'off'})
    submit = SubmitField('Import Leads', render_kw={'class': 'btn btn-success'})