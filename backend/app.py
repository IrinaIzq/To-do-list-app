"""
Main Flask application with improved structure and monitoring.
"""
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics
import logging
from datetime import datetime
from sqlalchemy import text
import os

from backend.database import db
from backend.config import get_config
from backend.routes import create_routes
from backend.services.auth_service import AuthService
from backend.services.task_service import TaskService
from backend.services.category_service import CategoryService


def create_app(config_name='development'):
    app = Flask(__name__, static_folder='../frontend', static_url_path='')

    # Load configuration
    config_class = get_config(config_name)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])

    # Prometheus
    if not app.config.get('TESTING', False):
        try:
            metrics = PrometheusMetrics(app)
            metrics.info('app_info', 'Application info', version=app.config['APP_VERSION'])
        except Exception as e:
            app.logger.warning(f'Failed to initialize Prometheus metrics: {e}')

    # Services
    auth_service = AuthService(
        secret_key=app.config['SECRET_KEY'],
        algorithm=app.config['JWT_ALGORITHM'],
        expiration_hours=app.config['JWT_EXPIRATION_HOURS']
    )
    task_service = TaskService()
    category_service = CategoryService()

    # Routes
    app.register_blueprint(
        create_routes(auth_service, task_service, category_service)
    )

    # Health
    @app.route('/health')
    def health_check():
        try:
            db.session.execute(text('SELECT 1'))
            db_status = 'healthy'
        except Exception as e:
            db_status = f'unhealthy: {str(e)}'

        return jsonify({
            'status': 'healthy' if db_status == 'healthy' else 'degraded',
            'timestamp': datetime.utcnow().isoformat(),
            'version': app.config['APP_VERSION'],
            'database': db_status,
            'environment': config_name
        })

    # Serve frontend
    @app.route('/')
    def root():
        return send_from_directory('../frontend', 'index.html')

    @app.route('/<path:path>')
    def static_proxy(path):
        return send_from_directory('../frontend', path)

    return app


def init_database(app):
    with app.app_context():
        db.create_all()
        app.logger.info('Database tables created')


if __name__ == "__main__":
    app = create_app()
    init_database(app)
    app.run(host="0.0.0.0", port=80)
