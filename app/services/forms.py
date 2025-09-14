"""Services forms."""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class ServiceForm(FlaskForm):
    """Form for adding/editing services."""

    name = StringField('Service Name', validators=[DataRequired()],
                       render_kw={'class': 'form-control', 'placeholder': 'Enter service name'})
    description = TextAreaField('Description', render_kw={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter service description (optional)'})
    submit = SubmitField('Save Service', render_kw={'class': 'btn btn-primary'})