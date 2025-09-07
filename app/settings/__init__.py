"""Settings blueprint for managing application settings."""

from flask import Blueprint

bp = Blueprint('settings', __name__)

from app.settings import routes