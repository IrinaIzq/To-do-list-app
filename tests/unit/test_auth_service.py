"""
Unit tests for AuthService.
"""
import pytest
from backend.services.auth_service import AuthService, AuthenticationError
from backend.database import User


class TestAuthService:
    """Test cases for AuthService."""
    
    def test_register_user_success(self, app, auth_service):
        """Test successful user registration."""
        with app.app_context():
            user = auth_service.register_user('newuser', 'password123')
            
            assert user is not None
            assert user.username == 'newuser'
            assert user.password_hash is not None
            assert user.password_hash != 'password123'
    
    def test_register_user_duplicate(self, app, auth_service, test_user):
        """Test registration with duplicate username."""
        with app.app_context():
            with pytest.raises(AuthenticationError, match="User already exists"):
                auth_service.register_user(test_user['username'], 'password')
    
    def test_register_user_missing_username(self, app, auth_service):
        """Test registration without username."""
        with app.app_context():
            with pytest.raises(AuthenticationError, match="Username and password are required"):
                auth_service.register_user('', 'password123')
    
    def test_register_user_missing_password(self, app, auth_service):
        """Test registration without password."""
        with app.app_context():
            with pytest.raises(AuthenticationError, match="Username and password are required"):
                auth_service.register_user('username', '')
    
    def test_register_user_short_password(self, app, auth_service):
        """Test registration with password too short."""
        with app.app_context():
            with pytest.raises(AuthenticationError, match="Password must be at least 6 characters"):
                auth_service.register_user('username', '12345')
    
    def test_authenticate_user_success(self, app, auth_service, test_user):
        """Test successful authentication."""
        with app.app_context():
            user = auth_service.authenticate_user(
                test_user['username'],
                test_user['password']
            )
            
            assert user is not None
            assert user.username == test_user['username']
    
    def test_authenticate_user_wrong_password(self, app, auth_service, test_user):
        """Test authentication with wrong password."""
        with app.app_context():
            user = auth_service.authenticate_user(
                test_user['username'],
                'wrongpassword'
            )
            
            assert user is None
    
    def test_authenticate_user_nonexistent(self, app, auth_service):
        """Test authentication with nonexistent user."""
        with app.app_context():
            user = auth_service.authenticate_user('nonexistent', 'password')
            
            assert user is None
    
    def test_generate_token(self, app, auth_service, test_user):
        """Test JWT token generation."""
        with app.app_context():
            token = auth_service.generate_token(test_user['id'])
            
            assert token is not None
            assert isinstance(token, str)
            assert len(token) > 0
    
    def test_verify_token_success(self, app, auth_service, test_user):
        """Test successful token verification."""
        with app.app_context():
            token = auth_service.generate_token(test_user['id'])
            user_id = auth_service.verify_token(token)
            
            assert user_id == test_user['id']
    
    def test_verify_token_invalid(self, app, auth_service):
        """Test verification of invalid token."""
        with app.app_context():
            with pytest.raises(AuthenticationError, match="Invalid token"):
                auth_service.verify_token('invalidtoken123')
    
    def test_verify_token_malformed(self, app, auth_service):
        """Test verification of malformed token."""
        with app.app_context():
            with pytest.raises(AuthenticationError):
                auth_service.verify_token('not.a.token')
    
    def test_get_user_by_id(self, app, auth_service, test_user):
        """Test getting user by ID."""
        with app.app_context():
            user = auth_service.get_user_by_id(test_user['id'])
            
            assert user is not None
            assert user.username == test_user['username']
    
    def test_get_user_by_id_not_found(self, app, auth_service):
        """Test getting nonexistent user by ID."""
        with app.app_context():
            user = auth_service.get_user_by_id(99999)
            
            assert user is None
    
    def test_password_hashing(self, app, auth_service):
        """Test that passwords are properly hashed."""
        with app.app_context():
            user = auth_service.register_user('hashtest', 'password123')
            
            # Password should be hashed
            assert user.password_hash != 'password123'
            # Hash should be long enough
            assert len(user.password_hash) > 50
            # Should be able to check password
            assert user.check_password('password123')
            assert not user.check_password('wrongpassword')