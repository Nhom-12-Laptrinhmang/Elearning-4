from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from ..config import config

# Use pbkdf2_sha256 (pure-Python) to avoid bcrypt binary issues on some platforms
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=int(config.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)


# DB-backed helpers. Import here to avoid circular imports at package import time
from typing import Optional
from ..database import Blog as BlogModel, Base, engine
from sqlalchemy.orm import Session


def get_user(db: Session, username: str) -> Optional[object]:
    try:
        from ..database import User as UserModel
    except Exception:
        return None
    return db.query(UserModel).filter(UserModel.username == username).first()


def create_user(db: Session, username: str, password: str):
    from ..database import User as UserModel
    hashed = hash_password(password)
    print("DEBUG: hashed password =", hashed)
    user = UserModel(username=username, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, username: str, password: str) -> bool:
    user = get_user(db, username)
    if not user:
        print("DEBUG: user not found")
        return False
    print("DEBUG: stored hash =", user.hashed_password)
    print("DEBUG: checking password =", password)
    return verify_password(password, user.hashed_password)

