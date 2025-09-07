"""Security utilities for the CRM application."""

import secrets
from datetime import datetime, timedelta
from functools import wraps

from flask import abort, current_app
from flask_login import current_user
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from app.models import UserRole


def require_role(required_role: UserRole):
    """Decorator to require a specific user role or higher."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if not current_user.has_permission(required_role):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_admin(f):
    """Decorator to require admin role."""
    return require_role(UserRole.ADMIN)(f)


def require_sales(f):
    """Decorator to require sales role or higher."""
    return require_role(UserRole.SALES)(f)


def require_ops(f):
    """Decorator to require ops role or higher."""
    return require_role(UserRole.OPS)(f)


def require_finance(f):
    """Decorator to require finance role or higher."""
    return require_role(UserRole.FINANCE)(f)


def generate_api_token(user_id: int, expiration: int = None) -> str:
    """Generate a secure API token for a user."""
    if expiration is None:
        expiration = current_app.config['API_TOKEN_EXPIRATION']
    
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps({
        'user_id': user_id,
        'exp': (datetime.utcnow() + timedelta(seconds=expiration)).timestamp()
    })


def verify_api_token(token: str) -> dict:
    """Verify an API token and return user info."""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        data = serializer.loads(token, max_age=current_app.config['API_TOKEN_EXPIRATION'])
        return data
    except (BadSignature, SignatureExpired):
        return None


def generate_password_reset_token(user_id: int) -> str:
    """Generate a password reset token."""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps({'user_id': user_id}, salt='password-reset')


def verify_password_reset_token(token: str, max_age: int = 3600) -> int:
    """Verify password reset token and return user ID."""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        data = serializer.loads(token, salt='password-reset', max_age=max_age)
        return data['user_id']
    except (BadSignature, SignatureExpired):
        return None


def generate_secure_filename(filename: str) -> str:
    """Generate a secure filename with random prefix."""
    if not filename:
        return f"{secrets.token_hex(8)}.file"
    
    # Split filename and extension
    parts = filename.rsplit('.', 1)
    if len(parts) == 2:
        name, ext = parts
        return f"{secrets.token_hex(8)}_{name[:50]}.{ext}"
    else:
        return f"{secrets.token_hex(8)}_{filename[:50]}"


def is_safe_filename(filename: str) -> bool:
    """Check if filename is safe to use."""
    if not filename:
        return False
    
    # Basic security checks
    dangerous_chars = ['..', '/', '\\', '<', '>', ':', '"', '|', '?', '*']
    return not any(char in filename for char in dangerous_chars)


def get_allowed_file_extensions() -> set:
    """Get allowed file extensions from config."""
    return current_app.config.get('ALLOWED_EXTENSIONS', set())


def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    if not filename:
        return False
    
    allowed_extensions = get_allowed_file_extensions()
    if not allowed_extensions:
        return True  # If no restrictions, allow all
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions