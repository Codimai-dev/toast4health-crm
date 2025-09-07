"""B2C Leads blueprint for managing B2C lead operations."""

from flask import Blueprint

bp = Blueprint('leads_b2c', __name__)

from app.leads_b2c import routes