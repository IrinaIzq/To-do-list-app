from backend.database import db
from backend.models.user import User
import jwt
from datetime import datetime, timedelta

class AuthenticationError(Exception):
    pass

class AuthService:
    def __init__(self, secret_key, algorithm, expiration_hours):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expiration_hours = expiration_hours

    def register_user(self, username, password):
        if not username or not password:
            raise AuthenticationError("Missing username or password")

        if User.query.filter_by(username=username).first():
            raise AuthenticationError("User already exists")

        user = User(username=username)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()
        return user

    def authenticate_user(self, username, password):
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            raise AuthenticationError("Invalid credentials")
        return user

    def generate_token(self, user_id):
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(hours=self.expiration_hours)
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token):
        try:
            data = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return data["user_id"]
        except Exception:
            raise AuthenticationError("Invalid token")

    def get_user_by_id(self, user_id):
        user = User.query.get(user_id)
        if not user:
            raise AuthenticationError("User not found")
        return user