from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..schemas import UserCreate, UserLogin, TokenResponse
from ..response import success_response, error_response
from ..services import auth_service
from ..database import get_db
from ..utils import get_current_user
from ..services.token_blacklist import add_to_blacklist

router = APIRouter()


@router.post("/register", response_model=dict)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    # Persist user into users table
    existing = auth_service.get_user(db, payload.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    user = auth_service.create_user(db, payload.username, payload.password)
    return success_response(data={"username": user.username}, message="User registered")


@router.post("/login", response_model=dict)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    # Validate credentials against DB
    if not auth_service.authenticate_user(db, payload.username, payload.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = auth_service.create_access_token({"sub": payload.username})
    return success_response(data={"access_token": access_token, "token_type": "bearer"}, message="Logged in")


@router.post("/revoke", response_model=dict)
def revoke_token(request: Request, db: Session = Depends(get_db)):
    """Low-level revoke: revoke token by raw Authorization header (keeps backward compatibility).
    Prefer calling /logout which requires a valid token and will revoke the current token.
    """
    auth_header = request.headers.get("authorization")
    if not auth_header:
        raise HTTPException(status_code=400, detail="Missing Authorization header")
    parts = auth_header.split()
    if len(parts) != 2:
        raise HTTPException(status_code=400, detail="Invalid Authorization header")
    raw_token = parts[1]
    add_to_blacklist(raw_token, db=db)
    return success_response(data=None, message="Token revoked")



@router.post("/logout", response_model=dict)
def logout(current_user: str = Depends(get_current_user), request: Request = None, db: Session = Depends(get_db)):
    """Logout current user by revoking the presented token. The token must be valid.
    This endpoint reads the Authorization header via dependency and blacklists that token.
    """
    # Extract raw token from header
    auth_header = request.headers.get("authorization") if request else None
    if not auth_header:
        raise HTTPException(status_code=400, detail="Missing Authorization header")
    parts = auth_header.split()
    if len(parts) != 2:
        raise HTTPException(status_code=400, detail="Invalid Authorization header")
    raw_token = parts[1]
    add_to_blacklist(raw_token, db=db)
    return success_response(data=None, message="Logged out")
