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

# Access control decorator
def require_module_access(module_name):
    """Decorator to check if user has access to a specific module."""
    def decorator(f):
        from functools import wraps
        from flask import flash, redirect, url_for
        from flask_login import current_user

        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))

            if not current_user.has_module_access(module_name):
                flash(f'Access denied. You do not have permission to access {module_name.replace("_", " ").title()}.', 'error')
                return redirect(url_for('dashboard.index'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator


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

    from app.camps import bp as camps_bp
    app.register_blueprint(camps_bp, url_prefix='/camps')

    from app.finance import bp as finance_bp
    app.register_blueprint(finance_bp, url_prefix='/finance')

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

    # Make UserRole enum available in templates
    from app.models import UserRole
    app.jinja_env.globals['UserRole'] = UserRole
    
    # Error handlers
    from app.errors import register_error_handlers
    register_error_handlers(app)

    # Auto-create database and seed if it doesn't exist
    with app.app_context():
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        if db_uri.startswith('sqlite:///'):
            db_file = db_uri[10:]  # Remove 'sqlite:///'
            db_path = os.path.join(app.instance_path, db_file) if not os.path.isabs(db_file) else db_file
            if not os.path.exists(db_path):
                from flask_migrate import upgrade
                upgrade()
                # Seed initial data inline
                from app.models import User, UserRole, Setting
                # Create admin user
                admin = User.query.filter_by(email='admin@toast4health.com').first()
                if not admin:
                    admin = User(
                        email='admin@toast4health.com',
                        full_name='System Administrator',
                        role=UserRole.ADMIN,
                        is_active=True
                    )
                    admin.set_password('toast4health')
                    db.session.add(admin)
                    print('Created admin user: admin@toast4health.com / toast4health')
                else:
                    print('Admin user already exists')

                # Seed Settings
                settings_data = [
                    # Sources
                    ('Source', 'website', 'Website', 1),
                    ('Source', 'referral', 'Referral', 2),
                    ('Source', 'social_media', 'Social Media', 3),
                    ('Source', 'direct_call', 'Direct Call', 4),
                    ('Source', 'walk_in', 'Walk-in', 5),
                    ('Source', 'advertisement', 'Advertisement', 6),
                    ('Source', 'other', 'Other', 7),

                    # Services
                    ('Services', 'consultation', 'Consultation', 1),
                    ('Services', 'treatment', 'Treatment', 2),
                    ('Services', 'therapy', 'Therapy', 3),
                    ('Services', 'wellness_program', 'Wellness Program', 4),
                    ('Services', 'health_checkup', 'Health Checkup', 5),
                    ('Services', 'fitness_training', 'Fitness Training', 6),
                    ('Services', 'nutrition_counseling', 'Nutrition Counseling', 7),

                    # Expense Main Categories
                    ('ExpenseMainCategory', 'company_expense', 'Company Expense', 1),
                    ('ExpenseMainCategory', 'booking', 'Booking', 2),

                    # Expense Sub Categories
                    ('ExpenseSubCategory', 'company_expense_rent', 'Rent', 1),
                    ('ExpenseSubCategory', 'company_expense_house_keeping', 'House Keeping', 2),
                    ('ExpenseSubCategory', 'company_expense_salary', 'Salary', 3),
                    ('ExpenseSubCategory', 'company_expense_employee_cost', 'Employee Cost', 4),
                    ('ExpenseSubCategory', 'booking_travelling', 'Travelling', 5),
                    ('ExpenseSubCategory', 'booking_food', 'Food', 6),
                    ('ExpenseSubCategory', 'booking_channel_partner', 'Channel Partner', 7),
                    ('ExpenseSubCategory', 'booking_employee_cost', 'Employee Cost', 8),

                    # Expense Categories (legacy)
                    ('ExpenseCategory', 'travel', 'Travel', 1),
                    ('ExpenseCategory', 'accommodation', 'Accommodation', 2),
                    ('ExpenseCategory', 'meals', 'Meals', 3),
                    ('ExpenseCategory', 'supplies', 'Supplies', 4),
                    ('ExpenseCategory', 'equipment', 'Equipment', 5),
                    ('ExpenseCategory', 'marketing', 'Marketing', 6),
                    ('ExpenseCategory', 'office', 'Office Expenses', 7),
                    ('ExpenseCategory', 'utilities', 'Utilities', 8),
                    ('ExpenseCategory', 'insurance', 'Insurance', 9),
                    ('ExpenseCategory', 'other', 'Other', 10),

                    # Employee Types
                    ('EmployeeType', 'full_time', 'Full Time', 1),
                    ('EmployeeType', 'part_time', 'Part Time', 2),
                    ('EmployeeType', 'contract', 'Contract', 3),
                    ('EmployeeType', 'consultant', 'Consultant', 4),
                    ('EmployeeType', 'intern', 'Intern', 5),

                    # Lead Status (for consistency)
                    ('LeadStatus', 'new', 'New', 1),
                    ('LeadStatus', 'follow_up', 'Follow Up', 2),
                    ('LeadStatus', 'prospect', 'Prospect', 3),
                    ('LeadStatus', 'converted', 'Converted', 4),
                    ('LeadStatus', 'lost', 'Lost', 5),
                ]

                for group, key, value, sort_order in settings_data:
                    existing_setting = Setting.query.filter_by(group=group, key=key).first()
                    if not existing_setting:
                        setting = Setting(
                            group=group,
                            key=key,
                            value=value,
                            sort_order=sort_order,
                            is_active=True,
                            created_by=admin.id if admin else None,
                            updated_by=admin.id if admin else None
                        )
                        db.session.add(setting)

                try:
                    db.session.commit()
                    print('Database seeded successfully!')
                except Exception as e:
                    db.session.rollback()
                    print(f'Error seeding database: {e}')

    # Main route - redirect to dashboard
    @app.route('/')
    def index():
        from flask import redirect, url_for
        from flask_login import current_user
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        return redirect(url_for('auth.login'))
    
    return app