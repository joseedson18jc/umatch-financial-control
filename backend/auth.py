from datetime import datetime, timedelta
from typing import Optional, List
"""Authentication helpers with optional dependency on python-jose.

This module tries to import JWTError and jwt from python-jose. If the
python-jose library is not installed, we fall back to a minimal JWT
implementation using base64 encoding. Note: this fallback is not secure
and should only be used in testing environments.
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
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

# Configuration
SECRET_KEY = "your-secret-key-keep-it-secret" # In production, use env var
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

__all__ = ['TOKEN', 'create_access_token', 'get_current_user', 'USERS_DB', 'verify_password', 'get_password_hash', 'ACCESS_TOKEN_EXPIRE_MINUTES']

# Admin Users (Hardcoded as requested)
# Using simple SHA256 hashing for passwords
import hashlib

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

USERS_DB = {
    "admin": {
        "password_hash": "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918", # admin
        "name": "Admin User"
    },
    "test": {
        "password_hash": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08", # test
        "name": "Test User"
    },
    "demo": {
        "password_hash": "2a97516c354b68848cdbd8f54a226a0a55b21ed138e207ad6c5cbb9c00aa5aea", # demo
        "name": "Demo User"
    }
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

def verify_password(plain_password, hashed_password):
    return hash_password(plain_password) == hashed_password

def get_password_hash(password):
    return hash_password(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
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
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = USERS_DB.get(token_data.username)
    if user is None:
        raise credentials_exception
    return user
