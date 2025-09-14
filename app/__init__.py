"""Flask CRM application initialization."""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from dotenv import load_dotenv

from config import config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app(config_name=None):
    """Create and configure the Flask application."""
    
    # Load environment variables
    load_dotenv()
    
    # Create Flask app
    app = Flask(__name__)
    
    # Configuration
    config_name = config_name or os.environ.get('FLASK_CONFIG', 'default')
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Configure Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))
    
    # Create upload folder if it doesn't exist
    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    # Register blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.dashboard import bp as dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    
    from app.leads_b2c import bp as leads_b2c_bp
    app.register_blueprint(leads_b2c_bp, url_prefix='/leads-b2c')
    
    from app.leads_b2b import bp as leads_b2b_bp
    app.register_blueprint(leads_b2b_bp, url_prefix='/leads-b2b')

    from app.follow_ups import bp as follow_ups_bp
    app.register_blueprint(follow_ups_bp, url_prefix='/follow-ups')

    from app.customers import bp as customers_bp
    app.register_blueprint(customers_bp, url_prefix='/customers')
    
    from app.bookings import bp as bookings_bp
    app.register_blueprint(bookings_bp, url_prefix='/bookings')
    
    from app.employees import bp as employees_bp
    app.register_blueprint(employees_bp, url_prefix='/employees')
    
    from app.expenses import bp as expenses_bp
    app.register_blueprint(expenses_bp, url_prefix='/expenses')
    
    from app.channel_partners import bp as channel_partners_bp
    app.register_blueprint(channel_partners_bp, url_prefix='/channel-partners')

    from app.services import bp as services_bp
    app.register_blueprint(services_bp, url_prefix='/services')

    from app.settings import bp as settings_bp
    app.register_blueprint(settings_bp, url_prefix='/settings')
    
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Register CLI commands
    from app.cli import register_cli_commands
    register_cli_commands(app)
    
    # Register template filters and globals
    from app.utils.filters import register_filters
    register_filters(app)
    
    # Error handlers
    from app.errors import register_error_handlers
    register_error_handlers(app)
    
    # Main route - redirect to dashboard
    @app.route('/')
    def index():
        from flask import redirect, url_for
        from flask_login import current_user
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        return redirect(url_for('auth.login'))
    
    return app