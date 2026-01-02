"""Employees forms."""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, DateField, SubmitField, DecimalField
from wtforms.validators import DataRequired, Email, Optional, Length, NumberRange

from app.models import Gender


class EmployeeForm(FlaskForm):
    """Form for adding/editing employees."""

    employee_code = StringField('Employee Code', validators=[DataRequired(), Length(max=20)],
                               render_kw={'class': 'form-control', 'readonly': True, 'autocomplete': 'off'})
    name = StringField('Full Name', validators=[DataRequired(), Length(max=100)],
                      render_kw={'class': 'form-control', 'placeholder': 'Enter full name', 'autocomplete': 'off'})
    contact_no = StringField('Contact Number', validators=[DataRequired(), Length(max=20)],
                            render_kw={'class': 'form-control', 'placeholder': 'Enter contact number', 'autocomplete': 'off'})
    email = StringField('Email', validators=[Optional(), Email(), Length(max=120)],
                       render_kw={'class': 'form-control', 'placeholder': 'Enter email (optional)', 'autocomplete': 'off'})
    designation = SelectField('Designation', validators=[Optional()],
                             render_kw={'class': 'form-select', 'autocomplete': 'off'})
    employ_type = SelectField('Employment Type', validators=[Optional()],
                             render_kw={'class': 'form-select', 'autocomplete': 'off'})
    gender = SelectField('Gender', choices=[('', 'Select Gender'), ('MALE', 'Male'), ('FEMALE', 'Female'), ('OTHER', 'Other')],
                        validators=[Optional()], render_kw={'class': 'form-select', 'autocomplete': 'off'})
    dob = DateField('Date of Birth', validators=[Optional()],
                    render_kw={'class': 'form-control', 'type': 'date', 'autocomplete': 'off'})
    degree = StringField('Degree', validators=[Optional(), Length(max=100)],
                        render_kw={'class': 'form-control', 'placeholder': 'Enter degree', 'autocomplete': 'off'})
    total_experience = DecimalField('Total Experience (Years)', validators=[Optional(), NumberRange(min=0, max=50, message='Experience must be between 0 and 50 years')],
                                  render_kw={'class': 'form-control no-scroll-number', 'placeholder': 'Enter experience in years (e.g., 2.5)', 'step': '0.1', 'min': '0', 'max': '50', 'autocomplete': 'off', 'onwheel': 'this.blur()'})
    whatsapp_no = StringField('WhatsApp Number', validators=[Optional(), Length(max=20)],
                             render_kw={'class': 'form-control', 'placeholder': 'Enter WhatsApp number', 'autocomplete': 'off'})
    aadhar_no = StringField('Aadhar Number', validators=[Optional(), Length(max=20)],
                           render_kw={'class': 'form-control', 'placeholder': 'Enter Aadhar number', 'autocomplete': 'off'})
    pan_no = StringField('PAN Number', validators=[Optional(), Length(max=20)],
                        render_kw={'class': 'form-control', 'placeholder': 'Enter PAN number', 'autocomplete': 'off'})
    bank_name = StringField('Bank Name', validators=[Optional(), Length(max=100)],
                           render_kw={'class': 'form-control', 'placeholder': 'Enter bank name', 'autocomplete': 'off'})
    branch_name = StringField('Branch Name', validators=[Optional(), Length(max=100)],
                             render_kw={'class': 'form-control', 'placeholder': 'Enter branch name', 'autocomplete': 'off'})
    account_no = StringField('Account Number', validators=[Optional(), Length(max=50)],
                            render_kw={'class': 'form-control', 'placeholder': 'Enter account number', 'autocomplete': 'off'})
    ifsc_code = StringField('IFSC Code', validators=[Optional(), Length(max=20)],
                           render_kw={'class': 'form-control', 'placeholder': 'Enter IFSC code', 'autocomplete': 'off'})
    temporary_address = TextAreaField('Temporary Address', validators=[Optional()],
                                     render_kw={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter temporary address', 'autocomplete': 'off'})
    permanent_address = TextAreaField('Permanent Address', validators=[Optional()],
                                     render_kw={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter permanent address', 'autocomplete': 'off'})
    skill_set = TextAreaField('Skill Set', validators=[Optional()],
                             render_kw={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter skill set', 'autocomplete': 'off'})
    employ_image = StringField('Employee Image', validators=[Optional(), Length(max=200)],
                              render_kw={'class': 'form-control', 'placeholder': 'Enter image URL or upload file below', 'autocomplete': 'off'})
    employ_image_file = FileField('Upload Image', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')],
                                 render_kw={'class': 'form-control', 'autocomplete': 'off'})
    submit = SubmitField('Save Employee', render_kw={'class': 'btn btn-primary'})