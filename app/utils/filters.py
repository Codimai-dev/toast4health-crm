"""Template filters for Jinja2."""

from datetime import datetime, date
from flask import current_app
from flask_wtf.csrf import generate_csrf


def format_currency(value):
    """Format a decimal value as currency."""
    if value is None:
        return "₹0.00"
    try:
        return f"₹{float(value):,.2f}"
    except (ValueError, TypeError):
        return "₹0.00"


def format_date(value, format='%d-%m-%Y'):
    """Format a date value."""
    if value is None:
        return ""
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, '%Y-%m-%d').date()
        except ValueError:
            return value
    if isinstance(value, datetime):
        value = value.date()
    if isinstance(value, date):
        return value.strftime(format)
    return str(value)


def format_datetime(value, format='%d-%m-%Y %I:%M %p'):
    """Format a datetime value."""
    if value is None:
        return ""
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return value
    if isinstance(value, datetime):
        return value.strftime(format)
    return str(value)


def truncate_text(text, length=50, suffix='...'):
    """Truncate text to specified length."""
    if not text:
        return ""
    if len(text) <= length:
        return text
    return text[:length].rstrip() + suffix


def status_badge_class(status):
    """Return Bootstrap badge class for status."""
    status_classes = {
        'NEW': 'bg-primary',
        'FOLLOW_UP': 'bg-warning',
        'PROSPECT': 'bg-info',
        'CONVERTED': 'bg-success',
        'LOST': 'bg-danger',
        'ACTIVE': 'bg-success',
        'INACTIVE': 'bg-secondary',
    }
    return status_classes.get(str(status).upper(), 'bg-secondary')


def role_badge_class(role):
    """Return Bootstrap badge class for user role."""
    role_classes = {
        'ADMIN': 'bg-danger',
        'SALES': 'bg-primary',
        'OPS': 'bg-info',
        'FINANCE': 'bg-success',
        'VIEWER': 'bg-secondary',
    }
    return role_classes.get(str(role).upper(), 'bg-secondary')


def get_dropdown_value(key, group=None):
    """
    Get the display value for a dropdown key from the Setting table.
    
    Args:
        key: The key to look up
        group: Optional group name to narrow the search
        
    Returns:
        The display value if found, otherwise the key itself with underscores replaced by spaces
    """
    if not key:
        return '-'
    
    from app.models import Setting
    
    try:
        if group:
            setting = Setting.query.filter_by(group=group, key=str(key)).first()
        else:
            # Search across all groups if no group specified
            setting = Setting.query.filter_by(key=str(key)).first()
        
        if setting:
            return setting.value
        else:
            # Fallback: return key with underscores replaced by spaces
            return str(key).replace('_', ' ')
    except Exception:
        # If any error occurs (like database not initialized), return the key
        return str(key).replace('_', ' ')


def register_filters(app):
    """Register custom filters and globals with Flask app."""
    app.jinja_env.filters['currency'] = format_currency
    app.jinja_env.filters['date'] = format_date
    app.jinja_env.filters['datetime'] = format_datetime
    app.jinja_env.filters['truncate_text'] = truncate_text
    app.jinja_env.filters['status_badge'] = status_badge_class
    app.jinja_env.filters['role_badge'] = role_badge_class
    app.jinja_env.filters['dropdown_value'] = get_dropdown_value

    # Add CSRF token global
    app.jinja_env.globals['csrf_token'] = generate_csrf