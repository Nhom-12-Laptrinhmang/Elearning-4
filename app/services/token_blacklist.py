from typing import Optional
from ..database import TokenBlacklist, SessionLocal
from sqlalchemy.orm import Session

# Simple in-memory blacklist
_in_memory_blacklist: set[str] = set()


def add_to_blacklist(token: str, db: Optional[Session] = None):
    """Add token string to in-memory set and persist to DB if db provided."""
    _in_memory_blacklist.add(token)
    if db is not None:
        # Try to persist
        try:
            existing = db.query(TokenBlacklist).filter(TokenBlacklist.token == token).first()
            if not existing:
                tb = TokenBlacklist(token=token)
                db.add(tb)
                db.commit()
        except Exception:
            # persistence is optional; swallow errors to avoid breaking logout
            db.rollback()


def is_blacklisted(token: str, db: Optional[Session] = None) -> bool:
    if token in _in_memory_blacklist:
        return True
    if db is not None:
        try:
            existing = db.query(TokenBlacklist).filter(TokenBlacklist.token == token).first()
            return existing is not None
        except Exception:
            return False
    return False


def clear_in_memory():
    _in_memory_blacklist.clear()
