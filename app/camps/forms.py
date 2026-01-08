"""Camp forms."""

from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional

from app.models import Employee, Setting


class CampForm(FlaskForm):
    """Form for adding/editing camp entries."""

    camp_id = StringField('Camp ID', validators=[DataRequired()],
                         render_kw={'class': 'form-control', 'autocomplete': 'off'})
    camp_date = DateField('Camp Date', validators=[DataRequired()],
                         render_kw={'class': 'form-control', 'autocomplete': 'off'})
    camp_location = StringField('Camp Location', validators=[DataRequired()],
                               render_kw={'class': 'form-control', 'placeholder': 'Enter camp location', 'autocomplete': 'off'})
    org_name = StringField('Org Name', validators=[Optional()],
                          render_kw={'class': 'form-control', 'placeholder': 'Enter organization name (optional)', 'autocomplete': 'off'})
    t4h_staff = SelectField('T4H Staff', validators=[Optional()],
                            render_kw={'class': 'form-select', 'autocomplete': 'off'})
    package = SelectField('Camp Package', choices=[], validators=[Optional()],
                         render_kw={'class': 'form-select', 'autocomplete': 'off'})
    diagnostic_partner = StringField('Diagnostic Partner', validators=[Optional()],
                                    render_kw={'class': 'form-control', 'placeholder': 'Enter diagnostic partner (optional)', 'autocomplete': 'off'})
    patient_name = StringField('Patient Name', validators=[DataRequired()],
                              render_kw={'class': 'form-control', 'placeholder': 'Enter patient name', 'autocomplete': 'off'})
    phone_no = StringField('Phone No', validators=[DataRequired()],
                          render_kw={'class': 'form-control', 'placeholder': 'Enter phone number', 'autocomplete': 'off'})
    age = StringField('Age', validators=[Optional()],
                     render_kw={'class': 'form-control', 'placeholder': 'Enter age', 'autocomplete': 'off'})
    gender = SelectField('Gender', choices=[('', 'Select Gender'), ('MALE', 'Male'), ('FEMALE', 'Female'), ('OTHER', 'Other')],
                        validators=[Optional()], render_kw={'class': 'form-select', 'autocomplete': 'off'})
    test_done = BooleanField('Test Done?', render_kw={'class': 'form-check-input'})
    submit = SubmitField('Save Camp Entry', render_kw={'class': 'btn btn-primary'})

    def __init__(self, *args, **kwargs):
        super(CampForm, self).__init__(*args, **kwargs)
        # Populate staff name choices from employees
        self.t4h_staff.choices = [('', 'Select Staff')] + [
            (str(emp.id), f"{emp.name} ({emp.employee_code})")
            for emp in Employee.query.filter_by().order_by(Employee.name).all()
        ]
        # Populate package choices from settings
        self.package.choices = [('', 'Select Package')] + [
            (setting.key, setting.value) 
            for setting in Setting.get_options('CampPackage')
        ]
