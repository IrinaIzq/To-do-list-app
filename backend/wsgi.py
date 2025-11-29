import os
from backend.app import create_app

# Lee FLASK_ENV (si existe) para seleccionar la configuración
config_name = os.environ.get("FLASK_ENV", os.environ.get("FLASK_CONFIG", "production"))
app = create_app(config_name)