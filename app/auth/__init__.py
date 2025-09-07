"""Authentication blueprint for user login, logout, and registration."""

from flask import Blueprint

bp = Blueprint('auth', __name__)

from app.auth import routes