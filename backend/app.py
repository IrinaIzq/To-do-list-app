from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics
import os
import logging
from datetime import datetime
from sqlalchemy import text

from backend.database import db
from backend.config import get_config
from backend.routes import create_routes
from backend.services.auth_service import AuthService
from backend.services.task_service import TaskService
from backend.services.category_service import CategoryService


def create_app(config_name='development'):
    app = Flask(__name__, static_folder='../frontend', static_url_path='')

    # Load config
    config_class = get_config(config_name)
    app.config.from_object(config_class)

    # Init extensions
    db.init_app(app)
    CORS(app, origins="*")

    # Prometheus
    if not app.config.get('TESTING', False):
        try:
            metrics = PrometheusMetrics(app)
            metrics.info('app_info', 'Application info', version=app.config['APP_VERSION'])
        except Exception as e:
            app.logger.warning(f'Failed to init Prometheus: {e}')

    # Services
    auth_service = AuthService(
        secret_key=app.config['SECRET_KEY'],
        algorithm=app.config['JWT_ALGORITHM'],
        expiration_hours=app.config['JWT_EXPIRATION_HOURS']
    )
    task_service = TaskService()
    category_service = CategoryService()

    # API routes
    app.register_blueprint(create_routes(auth_service, task_service, category_service))

    # HEALTH CHECK
    @app.route('/health')
    def health_check():
        try:
            db.session.execute(text('SELECT 1'))
            db_status = 'healthy'
        except Exception as e:
            db_status = f'unhealthy: {e}'
        return jsonify({
            'status': 'healthy' if db_status == 'healthy' else 'degraded',
            'database': db_status,
            'environment': config_name,
            'version': app.config['APP_VERSION'],
            'timestamp': datetime.utcnow().isoformat()
        })

    # SERVE FRONTEND (THIS IS THE IMPORTANT PART)
    @app.route('/')
    def serve_index():
        return send_from_directory('../frontend', 'index.html')

    @app.route('/<path:path>')
    def serve_static(path):
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