"""Services blueprint for managing service operations."""

from flask import Blueprint

bp = Blueprint('services', __name__)

from app.services import routes