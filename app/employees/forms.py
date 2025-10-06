"""Employees forms."""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, Email, Optional, Length

from app.models import Gender


class EmployeeForm(FlaskForm):
    """Form for adding/editing employees."""

    employee_code = StringField('Employee Code', validators=[DataRequired(), Length(max=20)],
                               render_kw={'class': 'form-control', 'readonly': True})
    name = StringField('Full Name', validators=[DataRequired(), Length(max=100)],
                      render_kw={'class': 'form-control', 'placeholder': 'Enter full name'})
    contact_no = StringField('Contact Number', validators=[DataRequired(), Length(max=20)],
                            render_kw={'class': 'form-control', 'placeholder': 'Enter contact number'})
    email = StringField('Email', validators=[Optional(), Email(), Length(max=120)],
                       render_kw={'class': 'form-control', 'placeholder': 'Enter email (optional)'})
    designation = StringField('Designation', validators=[Optional(), Length(max=100)],
                             render_kw={'class': 'form-control', 'placeholder': 'Enter designation'})
    employ_type = StringField('Employment Type', validators=[Optional(), Length(max=50)],
                             render_kw={'class': 'form-control', 'placeholder': 'Enter employment type'})
    gender = SelectField('Gender', choices=[('', 'Select Gender'), ('MALE', 'Male'), ('FEMALE', 'Female'), ('OTHER', 'Other')],
                        validators=[Optional()], render_kw={'class': 'form-select'})
    dob = DateField('Date of Birth', validators=[Optional()],
                    render_kw={'class': 'form-control', 'type': 'date'})
    degree = StringField('Degree', validators=[Optional(), Length(max=100)],
                        render_kw={'class': 'form-control', 'placeholder': 'Enter degree'})
    total_experience = StringField('Total Experience', validators=[Optional(), Length(max=50)],
                                  render_kw={'class': 'form-control', 'placeholder': 'Enter total experience'})
    whatsapp_no = StringField('WhatsApp Number', validators=[Optional(), Length(max=20)],
                             render_kw={'class': 'form-control', 'placeholder': 'Enter WhatsApp number'})
    aadhar_no = StringField('Aadhar Number', validators=[Optional(), Length(max=20)],
                           render_kw={'class': 'form-control', 'placeholder': 'Enter Aadhar number'})
    bank_name = StringField('Bank Name', validators=[Optional(), Length(max=100)],
                           render_kw={'class': 'form-control', 'placeholder': 'Enter bank name'})
    branch_name = StringField('Branch Name', validators=[Optional(), Length(max=100)],
                             render_kw={'class': 'form-control', 'placeholder': 'Enter branch name'})
    account_no = StringField('Account Number', validators=[Optional(), Length(max=50)],
                            render_kw={'class': 'form-control', 'placeholder': 'Enter account number'})
    ifsc_code = StringField('IFSC Code', validators=[Optional(), Length(max=20)],
                           render_kw={'class': 'form-control', 'placeholder': 'Enter IFSC code'})
    temporary_address = TextAreaField('Temporary Address', validators=[Optional()],
                                     render_kw={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter temporary address'})
    permanent_address = TextAreaField('Permanent Address', validators=[Optional()],
                                     render_kw={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter permanent address'})
    skill_set = TextAreaField('Skill Set', validators=[Optional()],
                             render_kw={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter skill set'})
    pdf_link = StringField('PDF Link', validators=[Optional(), Length(max=200)],
                          render_kw={'class': 'form-control', 'placeholder': 'Enter PDF link or upload file below'})
    employ_image = StringField('Employee Image', validators=[Optional(), Length(max=200)],
                              render_kw={'class': 'form-control', 'placeholder': 'Enter image URL or upload file below'})
    pdf_file = FileField('Upload PDF', validators=[Optional(), FileAllowed(['pdf'], 'PDF files only!')],
                        render_kw={'class': 'form-control'})
    employ_image_file = FileField('Upload Image', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')],
                                 render_kw={'class': 'form-control'})
    submit = SubmitField('Save Employee', render_kw={'class': 'btn btn-primary'})