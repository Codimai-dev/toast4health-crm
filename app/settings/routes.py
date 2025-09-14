"""Settings routes."""

from flask import render_template, jsonify, flash, redirect, url_for, request
from flask_login import login_required, current_user
from flask_wtf.csrf import validate_csrf, generate_csrf
from app import db
from app.models import (
    User, UserRole, B2CLead, B2BLead, FollowUp, Customer, Booking,
    Employee, Expense, ChannelPartner, Setting, AuditLog, Service
)
from app.settings import bp


@bp.route('/')
@login_required
def index():
    """Settings page with danger zone."""
    if not current_user.has_permission(UserRole.ADMIN):
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard.index'))

    return render_template('settings/index.html')


@bp.route('/delete-all-data', methods=['POST'])
@login_required
def delete_all_data():
    """Delete all application data (admin only)."""
    if not current_user.has_permission(UserRole.ADMIN):
        return jsonify({
            'success': False,
            'message': 'Access denied. Admin privileges required.'
        }), 403

    # Validate CSRF token from JSON data
    data = request.get_json() or {}
    csrf_token = data.get('csrf_token')
    if not csrf_token:
        return jsonify({
            'success': False,
            'message': 'CSRF token missing.'
        }), 400

    try:
        validate_csrf(csrf_token)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'CSRF validation failed.'
        }), 400

    try:
        # Delete in order to respect foreign key constraints
        # Start with dependent records first
        AuditLog.query.delete()
        FollowUp.query.delete()
        Expense.query.delete()
        Booking.query.delete()
        Customer.query.delete()
        B2CLead.query.delete()
        B2BLead.query.delete()
        Employee.query.delete()
        ChannelPartner.query.delete()
        Service.query.delete()
        Setting.query.delete()

        # Note: We don't delete users to keep at least the admin account
        # If you want to delete all users too, uncomment the next line:
        # User.query.delete()

        # Commit the changes
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'All application data has been successfully deleted.'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to delete data: {str(e)}'
        }), 500