"""Camps blueprint for managing health camp operations."""

from flask import Blueprint

bp = Blueprint('camps', __name__)

from app.camps import routes
