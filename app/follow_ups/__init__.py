"""Follow-ups module."""

from flask import Blueprint

bp = Blueprint('follow_ups', __name__)

from app.follow_ups import routes