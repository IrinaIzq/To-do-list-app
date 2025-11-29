# WSGI entrypoint for Gunicorn
from backend.app import create_app

# Create app instance for production
app = create_app()

if __name__ == "__main__":
    app.run()