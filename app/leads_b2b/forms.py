"""B2B Leads forms."""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SubmitField
from wtforms.validators import DataRequired, Email, Optional


class B2BLeadForm(FlaskForm):
    """Form for adding/editing B2B leads."""

    sr_no = StringField('Sr No', render_kw={'class': 'form-control', 'readonly': True})
    t4h_spoc = StringField('T4H SPOC', render_kw={'class': 'form-control', 'placeholder': 'Enter T4H SPOC (optional)'})
    date = DateField('Date', render_kw={'class': 'form-control'})
    organization_name = StringField('Organization Name', validators=[DataRequired()],
                                  render_kw={'class': 'form-control', 'placeholder': 'Enter organization name'})
    organization_email = StringField('Organization Email', validators=[Optional(), Email()],
                                   render_kw={'class': 'form-control', 'placeholder': 'Enter organization email (optional)'})
    location = StringField('Location', render_kw={'class': 'form-control', 'placeholder': 'Enter location (optional)'})
    type_of_leads = StringField('Type of Leads', render_kw={'class': 'form-control', 'placeholder': 'Enter type of leads (optional)'})
    org_poc_name_and_role = StringField('POC Name & Role', render_kw={'class': 'form-control', 'placeholder': 'Enter POC name and role (optional)'})
    employee_size = StringField('Employee Size', render_kw={'class': 'form-control', 'placeholder': 'Enter employee size (optional)'})
    employee_wellness_program = StringField('Employee Wellness Program', render_kw={'class': 'form-control', 'placeholder': 'Enter wellness program (optional)'})
    budget_of_wellness_program = StringField('Budget of Wellness Program', render_kw={'class': 'form-control', 'placeholder': 'Enter budget (optional)'})
    last_wellness_activity_done = StringField('Last Wellness Activity', render_kw={'class': 'form-control', 'placeholder': 'Enter last activity (optional)'})
    email1 = StringField('Email 1', validators=[Optional(), Email()], render_kw={'class': 'form-control', 'placeholder': 'Enter email 1 (optional)'})
    email2 = StringField('Email 2', validators=[Optional(), Email()], render_kw={'class': 'form-control', 'placeholder': 'Enter email 2 (optional)'})
    email3 = StringField('Email 3', validators=[Optional(), Email()], render_kw={'class': 'form-control', 'placeholder': 'Enter email 3 (optional)'})
    email4 = StringField('Email 4', validators=[Optional(), Email()], render_kw={'class': 'form-control', 'placeholder': 'Enter email 4 (optional)'})
    email5 = StringField('Email 5', validators=[Optional(), Email()], render_kw={'class': 'form-control', 'placeholder': 'Enter email 5 (optional)'})
    meeting1 = DateField('Meeting 1 Date', render_kw={'class': 'form-control'})
    meeting1_notes = TextAreaField('Meeting 1 Notes', render_kw={'class': 'form-control', 'rows': 2, 'placeholder': 'Enter meeting 1 notes (optional)'})
    meeting1_task_done = TextAreaField('Meeting 1 Task Done', render_kw={'class': 'form-control', 'rows': 2, 'placeholder': 'Enter meeting 1 tasks (optional)'})
    meeting2 = DateField('Meeting 2 Date', render_kw={'class': 'form-control'})
    notes = TextAreaField('Notes', render_kw={'class': 'form-control', 'rows': 2, 'placeholder': 'Enter notes (optional)'})
    task_done = TextAreaField('Task Done', render_kw={'class': 'form-control', 'rows': 2, 'placeholder': 'Enter tasks done (optional)'})
    status = StringField('Status', render_kw={'class': 'form-control', 'placeholder': 'Enter status (optional)'})
    submit = SubmitField('Save Lead', render_kw={'class': 'btn btn-primary'})