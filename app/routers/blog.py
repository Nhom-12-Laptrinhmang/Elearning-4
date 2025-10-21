from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List
from ..schemas import BlogCreate, BlogResponse, BlogUpdate
from ..response import success_response, error_response
from ..utils import get_current_user, save_upload
from ..database import get_db
from ..services import blog_service

router = APIRouter()

@router.get("/blog/search", response_model=dict)
def search_blog(q: str = Query(None), sort: str = Query("asc"), db: Session = Depends(get_db)):
    results = blog_service.search_blogs(db, q, sort)
    data = [{"id": b.id, "title": b.title, "content": b.content,
             "created_at": b.created_at, "updated_at": b.updated_at} for b in results]
    return success_response(data=data)

@router.post("/blog/create", response_model=dict)
def create_blog(payload: BlogCreate, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    blog = blog_service.create_blog(db, payload.title, payload.content)
    return success_response(data={"id": blog.id}, message="Blog created")


@router.get("/blogs/", response_model=dict)
def list_blogs(db: Session = Depends(get_db)):
    """Public: list all blogs"""
    results = blog_service.list_blogs(db)
    data = [{"id": b.id, "title": b.title, "content": b.content, "created_at": b.created_at, "updated_at": b.updated_at} for b in results]
    return success_response(data=data)


@router.get("/blog/all", response_model=dict)
def list_blogs_protected(current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """Protected: list all blogs (used by tests to check auth)"""
    results = blog_service.list_blogs(db)
    data = [{"id": b.id, "title": b.title, "content": b.content, "created_at": b.created_at, "updated_at": b.updated_at} for b in results]
    return success_response(data=data)


@router.get("/blog/{blog_id}", response_model=dict)
def get_blog(blog_id: int, db: Session = Depends(get_db)):
    blog = blog_service.get_blog(db, blog_id)
    if not blog:
        raise HTTPException(status_code=404, detail="Not found")
    return success_response(data={"id": blog.id, "title": blog.title, "content": blog.content, "created_at": blog.created_at, "updated_at": blog.updated_at})


@router.put("/blog/{blog_id}", response_model=dict)
def update_blog(blog_id: int, payload: BlogUpdate, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    blog = blog_service.update_blog(db, blog_id, payload.title, payload.content)
    if not blog:
        raise HTTPException(status_code=404, detail="Not found")
    return success_response(data={"id": blog.id}, message="Blog updated")


@router.delete("/blog/{blog_id}", response_model=dict)
def delete_blog(blog_id: int, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    ok = blog_service.delete_blog(db, blog_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Not found")
    return success_response(data=None, message="Blog deleted")


@router.post("/blog/upload", response_model=dict)
def upload_image(file: UploadFile = File(...), current_user: str = Depends(get_current_user)):
    path = save_upload(file)
    return success_response(data={"path": path}, message="File uploaded")




