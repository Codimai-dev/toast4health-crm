"""B2C Leads forms."""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, TextAreaField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Optional

from app.models import FollowUpOutcome, Service, Setting


class B2CLeadForm(FlaskForm):
    """Form for adding/editing B2C leads."""

    enquiry_id = StringField('Enquiry ID', validators=[DataRequired()],
                           render_kw={'class': 'form-control', 'readonly': True})
    customer_name = StringField('Customer Name', validators=[DataRequired()],
                              render_kw={'class': 'form-control', 'placeholder': 'Enter customer name'})
    contact_no = StringField('Contact Number', validators=[DataRequired()],
                           render_kw={'class': 'form-control', 'placeholder': 'Enter contact number'})
    email = StringField('Email', validators=[Optional(), Email()],
                       render_kw={'class': 'form-control', 'placeholder': 'Enter email (optional)'})
    enquiry_date = DateField('Enquiry Date', validators=[DataRequired()],
                           render_kw={'class': 'form-control'})
    source = SelectField('Source', choices=[], render_kw={'class': 'form-select'})
    services = SelectField('Services', choices=[], render_kw={'class': 'form-select'})
    referred_by = SelectField('Referred By', choices=[], render_kw={'class': 'form-select'})
    status = SelectField('Status', choices=[], default='NEW', render_kw={'class': 'form-select'})
    comment = TextAreaField('Comment', render_kw={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter comment (optional)'})
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
                           render_kw={'class': 'form-control'})
    notes = TextAreaField('Notes', render_kw={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter follow-up notes'})
    outcome = SelectField('Outcome', choices=[(outcome.value, outcome.value.replace('_', ' ')) for outcome in FollowUpOutcome],
                        validators=[DataRequired()], render_kw={'class': 'form-select'})
    next_follow_up_on = DateField('Next Follow-up Date', validators=[Optional()],
                                render_kw={'class': 'form-control'})
    submit = SubmitField('Add Follow-up', render_kw={'class': 'btn btn-primary'})


class CSVImportForm(FlaskForm):
    """Form for importing B2C leads from CSV."""

    csv_file = FileField('CSV File', validators=[FileRequired()],
                        render_kw={'class': 'form-control', 'accept': '.csv'})
    submit = SubmitField('Import Leads', render_kw={'class': 'btn btn-success'})