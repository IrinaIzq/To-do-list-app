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

    app = Flask(
        __name__,
        static_folder='../frontend',    # carpeta relativa dentro del contenedor
        static_url_path=''              # sirve estáticos desde la raíz
    )

    # Load configuration
    config_class = get_config(config_name)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    CORS(app, origins=app.config.get('CORS_ORIGINS', '*'))

    # Initialize Prometheus metrics ONLY if not testing
    if not app.config.get('TESTING', False):
        try:
            metrics = PrometheusMetrics(app)
            metrics.info('app_info', 'Application info',
                         version=app.config['APP_VERSION'])
        except Exception as e:
            app.logger.warning(f'Failed to initialize Prometheus metrics: {e}')

    # Initialize services
    auth_service = AuthService(
        secret_key=app.config['SECRET_KEY'],
        algorithm=app.config['JWT_ALGORITHM'],
        expiration_hours=app.config['JWT_EXPIRATION_HOURS']
    )
    task_service = TaskService()
    category_service = CategoryService()

    # Register blueprints
    app.register_blueprint(
        create_routes(auth_service, task_service, category_service)
    )

    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint for monitoring."""
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

    # ----------------------------
    # SERVIR FRONTEND (INDEX + STATIC)
    # ----------------------------
    # La carpeta frontend está en /app/frontend dentro del contenedor.
    # Usamos send_from_directory para servir index.html y los assets.
    FRONTEND_FOLDER = os.path.abspath(os.path.join(app.root_path, '..', 'frontend'))

    @app.route('/')
    def root():
        return send_from_directory(FRONTEND_FOLDER, 'index.html')

    @app.route('/<path:path>')
    def static_proxy(path):
        # intenta servir archivos estáticos (js/css/img). Si no existen, devuelve 404.
        return send_from_directory(FRONTEND_FOLDER, path)

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Internal error: {str(error)}')
        return jsonify({'error': 'Internal server error'}), 500

    # Configure logging
    if not app.debug:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    return app


def init_database(app):
    """Initialize database tables."""
    with app.app_context():
        db.create_all()
        app.logger.info('Database tables created')


if __name__ == "__main__":
    app = create_app()
    init_database(app)
    app.run(host="0.0.0.0", port=80)
