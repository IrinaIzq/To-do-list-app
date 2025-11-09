"""
Authentication service following Single Responsibility Principle.
Handles all authentication-related business logic.
"""
import jwt
import datetime
from typing import Optional, Tuple
from werkzeug.security import generate_password_hash, check_password_hash
from backend.database import db, User


class AuthenticationError(Exception):
    """Custom exception for authentication errors."""
    pass


class AuthService:
    """Service class for authentication operations."""
    
    def __init__(self, secret_key: str, algorithm: str = 'HS256', 
                 expiration_hours: int = 24):
        """
        Initialize authentication service.
        
        Args:
            secret_key: Secret key for JWT encoding
            algorithm: JWT algorithm to use
            expiration_hours: Token expiration time in hours
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expiration_hours = expiration_hours
    
    def register_user(self, username: str, password: str) -> User:
        """
        Register a new user.
        
        Args:
            username: Username for new user
            password: Password for new user
            
        Returns:
            Created User object
            
        Raises:
            AuthenticationError: If user already exists or validation fails
        """
        if not username or not password:
            raise AuthenticationError("Username and password are required")
        
        if len(password) < 6:
            raise AuthenticationError("Password must be at least 6 characters")
        
        if User.query.filter_by(username=username).first():
            raise AuthenticationError("User already exists")
        
        user = User(username=username)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return user
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate user with credentials.
        
        Args:
            username: Username to authenticate
            password: Password to verify
            
        Returns:
            User object if authentication successful, None otherwise
        """
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            return user
        
        return None
    
    def generate_token(self, user_id: int) -> str:
        """
        Generate JWT token for user.
        
        Args:
            user_id: ID of user to generate token for
            
        Returns:
            JWT token string
        """
        payload = {
            'user_id': user_id,
            'exp': datetime.datetime.utcnow() + 
                   datetime.timedelta(hours=self.expiration_hours),
            'iat': datetime.datetime.utcnow()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[int]:
        """
        Verify JWT token and extract user ID.
        
        Args:
            token: JWT token to verify
            
        Returns:
            User ID if token valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm]
            )
            return payload.get('user_id')
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: ID of user to retrieve
            
        Returns:
            User object if found, None otherwise
        """
        return User.query.get(user_id)