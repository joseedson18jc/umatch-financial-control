from datetime import datetime, timedelta
from typing import Optional, List
"""Authentication helpers with RBAC support.

This module provides:
- JWT-based authentication
- Role-based access control (admin/user)
- Password hashing with bcrypt (with SHA256 fallback)
- Admin guards for sensitive endpoints
"""
try:
    from jose import JWTError, jwt  # type: ignore
except ImportError:
    # Define fallback JWTError and minimal jwt functions
    class JWTError(Exception):
        """Fallback JWTError for environments without python-jose."""
        pass

    class _DummyJWT:
        def encode(self, payload: dict, secret: str, algorithm: str = 'HS256') -> str:
            import base64
            import json
            # Convert non-serializable objects (like datetime) to string for JSON serialization
            token = base64.urlsafe_b64encode(json.dumps(payload, default=str).encode()).decode()
            return token

        def decode(self, token: str, secret: str, algorithms: Optional[List[str]] = None) -> dict:
            import base64
            import json
            try:
                # Pad with '=' to correct length for base64 decoding
                padded = token + '=' * (-len(token) % 4)
                return json.loads(base64.urlsafe_b64decode(padded).decode())
            except Exception as e:
                raise JWTError(str(e))

    jwt = _DummyJWT()

import os
import hashlib
import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "development-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

__all__ = [
    'Token', 'create_access_token', 'get_current_user', 'require_admin',
    'USERS_DB', 'verify_password', 'get_password_hash', 'ACCESS_TOKEN_EXPIRE_MINUTES',
    'UserRole', 'is_admin'
]

# ============================================================================
# PASSWORD HASHING (bcrypt preferred, SHA256 fallback)
# ============================================================================

try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def hash_password(password: str) -> str:
        """Hash password using bcrypt."""
        return pwd_context.hash(password)
    
    def verify_password_hash(plain_password: str, hashed_password: str) -> bool:
        """Verify password against bcrypt hash."""
        # Support both bcrypt and legacy SHA256
        if hashed_password.startswith('$2'):  # bcrypt
            return pwd_context.verify(plain_password, hashed_password)
        else:  # SHA256 legacy
            return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password
    
    USING_BCRYPT = True
except ImportError:
    logger.warning("passlib not installed, using SHA256 for password hashing (not recommended for production)")
    
    def hash_password(password: str) -> str:
        """Hash password using SHA256 (fallback)."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password_hash(plain_password: str, hashed_password: str) -> bool:
        """Verify password against SHA256 hash."""
        return hash_password(plain_password) == hashed_password
    
    USING_BCRYPT = False


# ============================================================================
# ROLE-BASED ACCESS CONTROL
# ============================================================================

class UserRole:
    """User role constants."""
    ADMIN = "admin"
    USER = "user"


# ============================================================================
# USER DATABASE WITH ROLES
# ============================================================================

# Pre-hashed passwords (SHA256 for compatibility)
USERS_DB = {
    # Master Admin User (P0 requirement)
    "matheuscastrocorrea@gmail.com": {
        "password_hash": hashlib.sha256("123654".encode()).hexdigest(),  # 123654
        "name": "Master Admin",
        "role": UserRole.ADMIN,
        "force_password_reset": False  # Set to True for first login reset
    },
    # System Admin
    "admin@umatch.com": {
        "password_hash": "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918",  # admin
        "name": "Admin User",
        "role": UserRole.ADMIN,
        "force_password_reset": False
    },
    # Regular Users
    "test@umatch.com": {
        "password_hash": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",  # test
        "name": "Test User",
        "role": UserRole.USER,
        "force_password_reset": False
    },
    "demo@umatch.com": {
        "password_hash": "2a97516c354b68848cdbd8f54a226a0a55b21ed138e207ad6c5cbb9c00aa5aea",  # demo
        "name": "Demo User",
        "role": UserRole.USER,
        "force_password_reset": False
    }
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# ============================================================================
# MODELS
# ============================================================================

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None


class UserInfo(BaseModel):
    email: str
    name: str
    role: str


# ============================================================================
# AUTHENTICATION FUNCTIONS
# ============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against stored hash."""
    return verify_password_hash(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Get password hash for storage."""
    return hash_password(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token with user data including role."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = USERS_DB.get(username)
    if user is None:
        raise credentials_exception
    
    # Return user info with email
    return {
        "email": username,
        "name": user.get("name", "Unknown"),
        "role": user.get("role", UserRole.USER),
        "force_password_reset": user.get("force_password_reset", False)
    }


def is_admin(user: dict) -> bool:
    """Check if user has admin role."""
    return user.get("role") == UserRole.ADMIN


async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency that requires admin role.
    Use this on sensitive endpoints like:
    - deleteAll
    - bulkInsert
    - clearData
    - mappings management
    - AI admin actions
    """
    if not is_admin(current_user):
        logger.warning(f"Non-admin user {current_user.get('email')} attempted admin action")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required for this action"
        )
    return current_user


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_all_users() -> List[UserInfo]:
    """Get list of all users (admin function)."""
    return [
        UserInfo(email=email, name=data["name"], role=data.get("role", UserRole.USER))
        for email, data in USERS_DB.items()
    ]


def add_user(email: str, password: str, name: str, role: str = UserRole.USER) -> bool:
    """Add a new user to the database."""
    if email in USERS_DB:
        return False
    USERS_DB[email] = {
        "password_hash": get_password_hash(password),
        "name": name,
        "role": role,
        "force_password_reset": True
    }
    logger.info(f"Created new user: {email} with role {role}")
    return True
