import datetime
import jwt
from werkzeug.security import generate_password_hash, check_password_hash

from backend.database import db
from backend.models.user import User


# Exceptions required by tests
class AuthenticationError(Exception):
    """Base authentication error"""
    pass


class InvalidCredentialsError(AuthenticationError):
    """Raised when password or email is wrong"""
    pass


class TokenExpiredError(AuthenticationError):
    """Raised when JWT token is expired"""
    pass


class AuthService:
    def __init__(self, secret_key, algorithm="HS256", expiration_hours=24):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expiration_hours = expiration_hours


    # Registration
    def register(self, email, password):
        if not email or not password:
            raise InvalidCredentialsError("Email and password are required")

        if User.query.filter_by(email=email).first():
            raise InvalidCredentialsError("Email already registered")

        hashed = generate_password_hash(password)
        user = User(email=email, password=hashed)
        db.session.add(user)
        db.session.commit()

        return user


    # Login
    def login(self, email, password):
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            raise InvalidCredentialsError("Invalid credentials")

        return self._generate_token(user.id)


    # Token generation
    def _generate_token(self, user_id):
        expiration = datetime.datetime.utcnow() + datetime.timedelta(
            hours=self.expiration_hours
        )
        payload = {
            "user_id": user_id,
            "exp": expiration
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)


    # Token validation
    def verify_token(self, token):
        try:
            data = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")

        user = User.query.get(data.get("user_id"))
        if not user:
            raise AuthenticationError("User not found")

        return user