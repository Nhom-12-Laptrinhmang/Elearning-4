import jwt
from fastapi import HTTPException, Depends, UploadFile
from fastapi.security import HTTPBearer
from .config import config
from datetime import datetime, timedelta
from typing import Any
import os
from .database import get_db
from sqlalchemy.orm import Session
from .services.token_blacklist import is_blacklisted

security = HTTPBearer()


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)


def get_current_user(token: str = Depends(security), db: Session = Depends(get_db)):
    try:
        raw = token.credentials
        if is_blacklisted(raw, db=db):
            raise HTTPException(status_code=401, detail="Token has been revoked")
        payload = jwt.decode(raw, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def success_response(data: Any = None, message: str = "Success") -> dict:
    return {"status": "success", "message": message, "data": data}


def error_response(message: str = "Error", code: int = 400) -> dict:
    return {"status": "error", "message": message, "code": code}


def save_upload(file: UploadFile, upload_dir: str = "./uploads") -> str:
    """Save an UploadFile to a 'received' subfolder and return the relative saved path.

    Behavior changes made to avoid overwriting/accumulating uploaded test files in the
    top-level `uploads/` directory (which the test runner may read). New files are
    stored under `uploads/received/` and are given a short UUID-based name that keeps
    the original extension.
    """
    # ensure base upload dir exists, then store received files in a subfolder
    os.makedirs(upload_dir, exist_ok=True)
    received_dir = os.path.join(upload_dir, "received")
    os.makedirs(received_dir, exist_ok=True)

    # preserve extension, but use a short uuid-based filename to keep names short
    from uuid import uuid4
    _, ext = os.path.splitext(file.filename)
    ext = ext or ""
    filename = f"{uuid4().hex[:8]}{ext}"
    destination = os.path.join(received_dir, filename)
    with open(destination, "wb") as f:
        f.write(file.file.read())

    # return a relative path (uploads/received/<name>) for storing/displaying
    return os.path.join("uploads", "received", filename)