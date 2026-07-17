from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
import logging

from backend.database import get_db, row_to_dict, rows_to_list
from backend.services.auth_service import (
    verify_password, get_password_hash, create_access_token, 
    get_current_user, require_admin
)

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger("vaanisetu.auth_router")

class LoginRequest(BaseModel):
    username: str
    password: str

class AddUserRequest(BaseModel):
    username: str
    password: str
    role: str = "user"

@router.post("/login")
def login(req: LoginRequest):
    """Authenticate and return a JWT token."""
    with get_db() as conn:
        user = conn.execute(
            "SELECT username, password_hash, role FROM users WHERE username = ?",
            (req.username,)
        ).fetchone()
        
    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
        
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]}
    )
    return {"access_token": access_token, "token_type": "bearer", "role": user["role"]}

@router.get("/users")
def list_users(current_admin = Depends(require_admin)):
    """List all registered users (Admin only)."""
    with get_db() as conn:
        users = conn.execute("SELECT username, role, created_at FROM users").fetchall()
    return rows_to_list(users)

@router.post("/users")
def add_user(req: AddUserRequest, current_admin = Depends(require_admin)):
    """Create a new user (Admin only)."""
    if req.role not in ("admin", "user"):
        raise HTTPException(status_code=400, detail="Invalid role. Must be 'admin' or 'user'.")
        
    now = datetime.utcnow().isoformat()
    hashed = get_password_hash(req.password)
    
    with get_db() as conn:
        existing = conn.execute("SELECT username FROM users WHERE username = ?", (req.username,)).fetchone()
        if existing:
            raise HTTPException(status_code=400, detail="Username already exists")
            
        conn.execute(
            "INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
            (req.username, hashed, req.role, now)
        )
    logger.info(f"Admin {current_admin['username']} created new {req.role}: {req.username}")
    return {"message": f"User {req.username} created successfully"}
