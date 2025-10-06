"""CLI commands for the CRM application."""

import click
from datetime import date, datetime
from flask.cli import with_appcontext

from app import db
from app.models import User, UserRole, Setting, AuditLog


@click.command()
@with_appcontext
def seed():
    """Seed the database with initial data."""
    click.echo('Seeding database...')
    
    # Create admin user
    admin = User.query.filter_by(email='admin@example.com').first()
    if not admin:
        admin = User(
            email='admin@example.com',
            full_name='System Administrator',
            role=UserRole.ADMIN,
            is_active=True
        )
        admin.set_password('Admin@12345')
        db.session.add(admin)
        click.echo('Created admin user: admin@example.com / Admin@12345')
    else:
        click.echo('Admin user already exists')
    
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
                created_by=admin.id,
                updated_by=admin.id
            )
            db.session.add(setting)
    
    try:
        db.session.commit()
        click.echo('Database seeded successfully!')
    except Exception as e:
        db.session.rollback()
        click.echo(f'Error seeding database: {e}')


@click.command()
@click.argument('filepath')
@with_appcontext
def import_xlsx(filepath):
    """Import data from XLSX file."""
    click.echo(f'Importing data from {filepath}...')
    
    try:
        import pandas as pd
        from app.utils.importers import import_from_excel
        
        result = import_from_excel(filepath)
        click.echo(f'Import completed: {result}')
    except ImportError:
        click.echo('Error: pandas is required for XLSX import')
    except Exception as e:
        click.echo(f'Error importing data: {e}')


@click.command()
@with_appcontext
def init_db():
    """Initialize the database."""
    click.echo('Initializing database...')
    db.create_all()
    click.echo('Database initialized!')


@click.command()
@with_appcontext
def reset_db():
    """Reset the database (WARNING: This will delete all data!)."""
    if click.confirm('This will delete all data. Are you sure?'):
        click.echo('Resetting database...')
        db.drop_all()
        db.create_all()
        click.echo('Database reset complete!')
    else:
        click.echo('Database reset cancelled.')


@click.command()
@click.option('--email', prompt=True, help='User email')
@click.option('--password', prompt=True, hide_input=True, help='User password')
@click.option('--name', prompt=True, help='Full name')
@click.option('--role', type=click.Choice(['ADMIN', 'SALES', 'OPS', 'FINANCE', 'VIEWER']), 
              default='VIEWER', help='User role')
@with_appcontext
def create_user(email, password, name, role):
    """Create a new user."""
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        click.echo('User with this email already exists!')
        return
    
    user = User(
        email=email,
        full_name=name,
        role=UserRole[role],
        is_active=True
    )
    user.set_password(password)
    
    db.session.add(user)
    try:
        db.session.commit()
        click.echo(f'User created successfully: {email}')
    except Exception as e:
        db.session.rollback()
        click.echo(f'Error creating user: {e}')


@click.command()
@with_appcontext
def list_users():
    """List all users."""
    users = User.query.all()
    if not users:
        click.echo('No users found.')
        return
    
    click.echo('Users:')
    for user in users:
        status = 'Active' if user.is_active else 'Inactive'
        click.echo(f'  {user.email} - {user.full_name} ({user.role.value}) [{status}]')


def register_cli_commands(app):
    """Register CLI commands with Flask app."""
    app.cli.add_command(seed)
    app.cli.add_command(import_xlsx)
    app.cli.add_command(init_db)
    app.cli.add_command(reset_db)
    app.cli.add_command(create_user)
    app.cli.add_command(list_users)