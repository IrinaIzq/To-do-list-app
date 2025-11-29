import jwt
from datetime import datetime, timedelta
from backend.database import db
from backend.models.user import User


class AuthenticationError(Exception):
    pass


class RegistrationError(Exception):
    pass


class AuthService:

    # Exponer excepciones como atributos de clase (los tests lo requieren)
    AuthenticationError = AuthenticationError
    RegistrationError = RegistrationError

    def __init__(self, secret_key, algorithm, expiration_hours):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expiration_hours = expiration_hours

    def register_user(self, username, password):
        if not username or not username.strip():
            raise RegistrationError("Username and password are required")

        if not password:
            raise RegistrationError("Username and password are required")

        if len(password) < 6:
            raise RegistrationError("Password must be at least 6 characters")

        existing = User.query.filter_by(username=username).first()
        if existing:
            raise RegistrationError("User already exists")

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
        exp = datetime.utcnow() + timedelta(hours=self.expiration_hours)
        return jwt.encode({"user_id": user_id, "exp": exp}, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token):
        try:
            data = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return data["user_id"]
        except Exception:
            raise AuthenticationError("Invalid token")

    def get_user_by_id(self, user_id):
        return User.query.get(user_id)