"""Channel Partners blueprint for managing channel partner operations."""

from flask import Blueprint

bp = Blueprint('channel_partners', __name__)

from app.channel_partners import routes