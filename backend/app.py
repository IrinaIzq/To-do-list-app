"""
Main Flask application
"""
import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics
import logging
from datetime import datetime
from sqlalchemy import text

from backend.database import db, init_models
from backend.config import get_config
from backend.routes import create_routes
from backend.services.auth_service import AuthService
from backend.services.task_service import TaskService
from backend.services.category_service import CategoryService

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'production')
    app = Flask(__name__, static_folder=None)  # we'll serve static manually
    config_class = get_config(config_name)
    app.config.from_object(config_class)

    # extensions
    db.init_app(app)
    CORS(app, origins=app.config.get('CORS_ORIGINS', ['*']))

    # prometheus (optional)
    if not app.config.get('TESTING', False):
        try:
            metrics = PrometheusMetrics(app)
            metrics.info('app_info', 'Application info', version=app.config['APP_VERSION'])
        except Exception as e:
            app.logger.warning(f'Prometheus init failed: {e}')

    # services
    auth_service = AuthService(
        secret_key=app.config['SECRET_KEY'],
        algorithm=app.config['JWT_ALGORITHM'],
        expiration_hours=app.config['JWT_EXPIRATION_HOURS']
    )
    task_service = TaskService()
    category_service = CategoryService()

    # register routes / blueprint
    app.register_blueprint(create_routes(auth_service, task_service, category_service))

    # health
    @app.route('/health')
    def health_check():
        try:
            # use text() when using raw SQL in SQLAlchemy
            with app.app_context():
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

    # Serve frontend index at root
    @app.route('/', methods=['GET'])
    def root_index():
        frontend_path = os.path.join(app.root_path, '..', 'frontend')
        return send_from_directory(frontend_path, 'index.html')

    # optional: serve static assets from /static path (css/js)
    @app.route('/static/<path:filename>')
    def static_files(filename):
        frontend_path = os.path.join(app.root_path, '..', 'frontend')
        return send_from_directory(frontend_path, filename)

    # logging config
    if not app.debug:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    return app

# create module-level app so wsgi import works
app = create_app(os.environ.get('FLASK_ENV', 'production'))

def init_database(app_instance):
    with app_instance.app_context():
        init_models()
        db.create_all()
        app_instance.logger.info('Database tables created')

if __name__ == "__main__":
    init_database(app)
    app.run(host="0.0.0.0", port=80)