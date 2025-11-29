# WSGI entrypoint for Gunicorn
import os
from backend.app import create_app

# Force production environment for Azure
os.environ.setdefault('FLASK_ENV', 'production')

# Create app instance for production
app = create_app('production')  # ← Forzar 'production' explícitamente

if __name__ == "__main__":
    app.run()