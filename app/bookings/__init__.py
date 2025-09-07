"""Bookings blueprint for managing booking operations."""

from flask import Blueprint

bp = Blueprint('bookings', __name__)

from app.bookings import routes