"""Error handlers for the CRM application."""

from flask import render_template, jsonify, request
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):
    """Register error handlers with the Flask app."""
    
    @app.errorhandler(403)
    def forbidden(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Forbidden', 'message': 'Insufficient permissions'}), 403
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Not Found', 'message': 'Resource not found'}), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Server Error: {error}')
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal Server Error', 'message': 'An unexpected error occurred'}), 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        if request.path.startswith('/api/'):
            return jsonify({
                'error': error.name,
                'message': error.description,
                'code': error.code
            }), error.code
        return render_template('errors/generic.html', error=error), error.code