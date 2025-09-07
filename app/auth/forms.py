"""Authentication forms."""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from app.models import User, UserRole


class LoginForm(FlaskForm):
    """User login form."""
    
    email = StringField('Email', validators=[DataRequired(), Email()], 
                       render_kw={'class': 'form-control', 'placeholder': 'Enter your email'})
    password = PasswordField('Password', validators=[DataRequired()],
                           render_kw={'class': 'form-control', 'placeholder': 'Enter your password'})
    remember_me = BooleanField('Remember Me', render_kw={'class': 'form-check-input'})
    submit = SubmitField('Sign In', render_kw={'class': 'btn btn-primary w-100'})


class RegistrationForm(FlaskForm):
    """User registration form."""
    
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)],
                           render_kw={'class': 'form-control', 'placeholder': 'Enter your full name'})
    email = StringField('Email', validators=[DataRequired(), Email()],
                       render_kw={'class': 'form-control', 'placeholder': 'Enter your email'})
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ], render_kw={'class': 'form-control', 'placeholder': 'Choose a strong password'})
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ], render_kw={'class': 'form-control', 'placeholder': 'Confirm your password'})
    role = SelectField('Role', validators=[DataRequired()], 
                      choices=[(role.value, role.value.title()) for role in UserRole if role != UserRole.ADMIN],
                      render_kw={'class': 'form-select'})
    submit = SubmitField('Register', render_kw={'class': 'btn btn-primary w-100'})
    
    def validate_email(self, email):
        """Check if email is already registered."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email is already registered. Please use a different email.')


class ResetPasswordRequestForm(FlaskForm):
    """Password reset request form."""
    
    email = StringField('Email', validators=[DataRequired(), Email()],
                       render_kw={'class': 'form-control', 'placeholder': 'Enter your email'})
    submit = SubmitField('Request Password Reset', render_kw={'class': 'btn btn-primary w-100'})


class ResetPasswordForm(FlaskForm):
    """Password reset form."""
    
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ], render_kw={'class': 'form-control', 'placeholder': 'Enter new password'})
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ], render_kw={'class': 'form-control', 'placeholder': 'Confirm new password'})
    submit = SubmitField('Reset Password', render_kw={'class': 'btn btn-primary w-100'})


class ChangePasswordForm(FlaskForm):
    """Change password form."""
    
    current_password = PasswordField('Current Password', validators=[DataRequired()],
                                   render_kw={'class': 'form-control', 'placeholder': 'Enter current password'})
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ], render_kw={'class': 'form-control', 'placeholder': 'Enter new password'})
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ], render_kw={'class': 'form-control', 'placeholder': 'Confirm new password'})
    submit = SubmitField('Change Password', render_kw={'class': 'btn btn-primary'})