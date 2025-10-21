from ..database import Blog as BlogModel
from sqlalchemy.orm import Session
from typing import List, Optional


def create_blog(db: Session, title: str, content: str) -> BlogModel:
    blog = BlogModel(title=title, content=content)
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return blog


def get_blog(db: Session, blog_id: int) -> Optional[BlogModel]:
    return db.query(BlogModel).filter(BlogModel.id == blog_id).first()


def update_blog(db: Session, blog_id: int, title: str | None = None, content: str | None = None) -> Optional[BlogModel]:
    blog = get_blog(db, blog_id)
    if not blog:
        return None
    if title is not None:
        blog.title = title
    if content is not None:
        blog.content = content
    db.commit()
    db.refresh(blog)
    return blog


def delete_blog(db: Session, blog_id: int) -> bool:
    blog = get_blog(db, blog_id)
    if not blog:
        return False
    db.delete(blog)
    db.commit()
    return True


def search_blogs(db: Session, q: str | None, sort: str = "asc") -> List[BlogModel]:
    query = db.query(BlogModel)
    if q:
        query = query.filter((BlogModel.title.contains(q)) | (BlogModel.content.contains(q)))
    if sort.lower() == "asc":
        query = query.order_by(BlogModel.created_at.asc())
    else:
        query = query.order_by(BlogModel.created_at.desc())
    return query.all()


def list_blogs(db: Session) -> List[BlogModel]:
    """Return all blogs ordered by created_at descending"""
    return db.query(BlogModel).order_by(BlogModel.created_at.desc()).all()
