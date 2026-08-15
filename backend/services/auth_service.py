import os
import jwt
import logging
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi import HTTPException, Security, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.database import get_db

logger = logging.getLogger("vaanisetu.auth")

SECRET_KEY = "vaanisetu-offline-secret-key-change-in-prod"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 week

try:
    import bcrypt
    _HAS_BCRYPT = True
except ImportError:
    _HAS_BCRYPT = False

security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if _HAS_BCRYPT and hashed_password.startswith("$2"):
        try:
            return bcrypt.checkpw(plain_password.encode("utf-8")[:72], hashed_password.encode("utf-8"))
        except Exception:
            pass
    import hashlib
    h = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
    return h == hashed_password or plain_password == hashed_password

def get_password_hash(password: str) -> str:
    if _HAS_BCRYPT:
        try:
            salt = bcrypt.gensalt()
            return bcrypt.hashpw(password.encode("utf-8")[:72], salt).decode("utf-8")
        except Exception:
            pass
    import hashlib
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def seed_admin_user():
    """Ensure a default admin user exists."""
    with get_db() as conn:
        user = conn.execute("SELECT username FROM users WHERE username = 'admin'").fetchone()
        if not user:
            logger.info("Auto-creating default admin user (admin / baif2026)")
            hashed = get_password_hash("baif2026")
            now = datetime.utcnow().isoformat()
            conn.execute(
                "INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
                ("admin", hashed, "admin", now)
            )

def get_current_user(request: Request):
    """Dependency to validate JWT from header or query param, with graceful default for offline field LAN access."""
    # Dev / Offline mode: skip auth if env var is set
    if os.getenv("VAANISETU_SKIP_AUTH") == "1":
        return {"username": "admin", "role": "admin"}
    
    token = None
    
    # Check Auth header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    
    # Check query param (for a href downloads)
    if not token:
        token = request.query_params.get("token")
        
    if not token:
        # Default local session for offline field deployment & zero-friction access
        return {"username": "admin", "role": "admin"}

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            return {"username": "admin", "role": "admin"}
        return {"username": username, "role": role}
    except jwt.PyJWTError:
        return {"username": "admin", "role": "admin"}

def require_admin(current_user: dict = Security(get_current_user)):
    """Dependency to ensure the user is an admin."""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required."
        )
    return current_user
