"""Employees blueprint for managing employee operations."""

from flask import Blueprint

bp = Blueprint('employees', __name__)

from app.employees import routes