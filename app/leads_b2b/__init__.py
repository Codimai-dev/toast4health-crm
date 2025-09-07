"""B2B Leads blueprint for managing B2B lead operations."""

from flask import Blueprint

bp = Blueprint('leads_b2b', __name__)

from app.leads_b2b import routes