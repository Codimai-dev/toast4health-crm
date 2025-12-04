"""B2B Leads forms."""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SubmitField
from wtforms.validators import DataRequired, Email, Optional


class B2BLeadForm(FlaskForm):
    """Form for adding/editing B2B leads."""

    sr_no = StringField('Sr No', render_kw={'class': 'form-control', 'readonly': True, 'autocomplete': 'off'})
    t4h_spoc = StringField('T4H SPOC', render_kw={'class': 'form-control', 'placeholder': 'Enter T4H SPOC (optional)', 'autocomplete': 'off'})
    date = DateField('Date', render_kw={'class': 'form-control', 'autocomplete': 'off'})
    organization_name = StringField('Organization Name', validators=[DataRequired()],
                                  render_kw={'class': 'form-control', 'placeholder': 'Enter organization name', 'autocomplete': 'off'})
    organization_email = StringField('Organization Email', validators=[Optional(), Email()],
                                   render_kw={'class': 'form-control', 'placeholder': 'Enter organization email (optional)', 'autocomplete': 'off'})
    location = StringField('Location', render_kw={'class': 'form-control', 'placeholder': 'Enter location (optional)', 'autocomplete': 'off'})
    type_of_leads = StringField('Type of Leads', render_kw={'class': 'form-control', 'placeholder': 'Enter type of leads (optional)', 'autocomplete': 'off'})
    org_poc_name_and_role = StringField('POC Name & Role', render_kw={'class': 'form-control', 'placeholder': 'Enter POC name and role (optional)', 'autocomplete': 'off'})
    employee_size = StringField('Employee Size', render_kw={'class': 'form-control', 'placeholder': 'Enter employee size (optional)', 'autocomplete': 'off'})
    employee_wellness_program = StringField('Employee Wellness Program', render_kw={'class': 'form-control', 'placeholder': 'Enter wellness program (optional)', 'autocomplete': 'off'})
    budget_of_wellness_program = StringField('Budget of Wellness Program', render_kw={'class': 'form-control', 'placeholder': 'Enter budget (optional)', 'autocomplete': 'off'})
    last_wellness_activity_done = StringField('Last Wellness Activity', render_kw={'class': 'form-control', 'placeholder': 'Enter last activity (optional)', 'autocomplete': 'off'})
    submit = SubmitField('Save Lead', render_kw={'class': 'btn btn-primary'})


class MeetingForm(FlaskForm):
    """Form for adding meetings to B2B leads."""

    meeting1_date = DateField('Meeting 1 Date', render_kw={'class': 'form-control', 'autocomplete': 'off'})
    meeting2_date = DateField('Meeting 2 Date', render_kw={'class': 'form-control', 'autocomplete': 'off'})
    meeting1_notes = TextAreaField('Meeting 1 Notes', render_kw={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter meeting 1 notes (optional)', 'autocomplete': 'off'})
    meeting1_task_done = TextAreaField('Meeting 1 Task Done', render_kw={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter meeting 1 tasks done (optional)', 'autocomplete': 'off'})
    notes = TextAreaField('Notes', render_kw={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter general notes (optional)', 'autocomplete': 'off'})
    task_done = TextAreaField('Task Done', render_kw={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter tasks done (optional)', 'autocomplete': 'off'})
    status = StringField('Status', render_kw={'class': 'form-control', 'placeholder': 'Enter status (optional)', 'autocomplete': 'off'})
    submit = SubmitField('Save Meeting', render_kw={'class': 'btn btn-primary'})