"""Customers blueprint for managing customer operations."""

from flask import Blueprint

bp = Blueprint('customers', __name__)

from app.customers import routes