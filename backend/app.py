"""
Main Flask application with improved structure and monitoring.
"""
from flask import Flask, jsonify
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics
import logging
from datetime import datetime

from backend.database import db
from backend.config import get_config
from backend.routes import create_routes
from backend.services.auth_service import AuthService
from backend.services.task_service import TaskService
from backend.services.category_service import CategoryService


def create_app(config_name='development'):
    """
    Application factory pattern for creating Flask app.
    
    Args:
        config_name: Configuration environment name
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    config_class = get_config(config_name)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Initialize Prometheus metrics ONLY if not testing
    if not app.config.get('TESTING', False):
        try:
            metrics = PrometheusMetrics(app)
            # Add custom metrics
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
            # Check database connection
            db.session.execute('SELECT 1')
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
    
    # Root endpoint
    @app.route('/')
    def home():
        """Root endpoint."""
        return jsonify({
            'name': app.config['APP_NAME'],
            'version': app.config['APP_VERSION'],
            'status': 'running'
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
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
    app.run(debug=True, host='0.0.0.0', port=5000)