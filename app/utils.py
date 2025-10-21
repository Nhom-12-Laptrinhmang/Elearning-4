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
    """Save an UploadFile to the upload_dir and return the saved path."""
    os.makedirs(upload_dir, exist_ok=True)
    filename = f"{int(datetime.utcnow().timestamp())}_{file.filename}"
    destination = os.path.join(upload_dir, filename)
    with open(destination, "wb") as f:
        f.write(file.file.read())
    return destination