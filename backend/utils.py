import jwt
import datetime
from flask import request, jsonify
from functools import wraps

SECRET_KEY = "mysecretkey"  # ⚠️ cámbialo en producción

def generate_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
        if not token:
            return jsonify({"error": "Token is missing"}), 401
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user_id = data["user_id"]
        except:
            return jsonify({"error": "Invalid or expired token"}), 401
        return f(current_user_id, *args, **kwargs)
    return decorated