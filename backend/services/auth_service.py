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

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

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
    """Dependency to validate JWT from header or query param and return current user."""
    # Dev mode: skip auth if env var is set
    if os.getenv("VAANISETU_SKIP_AUTH") == "1":
        logger.warning("⚠️  DEV MODE: Auth bypassed (VAANISETU_SKIP_AUTH=1)")
        return {"username": "dev", "role": "admin"}
    
    token = None
    
    # Check Auth header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    
    # Check query param (for a href downloads)
    if not token:
        token = request.query_params.get("token")
        
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    return {"username": username, "role": role}

def require_admin(current_user: dict = Security(get_current_user)):
    """Dependency to ensure the user is an admin."""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required."
        )
    return current_user
