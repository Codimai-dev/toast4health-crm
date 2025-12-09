"""Main application entry point for the Flask CRM."""

import os
from app import create_app, db
from app.models import *  # Import all models for Flask-Migrate

# Create the Flask application
app = create_app(os.environ.get('FLASK_CONFIG'))


@app.shell_context_processor
def make_shell_context():
    """Make database instance and models available in Flask shell."""
    return {
        'db': db,
        'User': User,
        'B2CLead': B2CLead,
        'B2BLead': B2BLead,
        'FollowUp': FollowUp,
        'Customer': Customer,
        'Booking': Booking,
        'Employee': Employee,
        'Expense': Expense,
        'ChannelPartner': ChannelPartner,
        'Setting': Setting,
        'Camp': Camp,
        'AuditLog': AuditLog
    }


if __name__ == '__main__':
    app.run(debug=True)