"""API routes."""

from app.api import bp


@bp.route('/')
def index():
    """Placeholder route for API blueprint."""
    return "API module"