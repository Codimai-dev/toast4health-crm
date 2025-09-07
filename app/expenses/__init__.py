"""Expenses blueprint for managing expense operations."""

from flask import Blueprint

bp = Blueprint('expenses', __name__)

from app.expenses import routes