from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class BlogBase(BaseModel):
    title: str
    content: str


class BlogCreate(BlogBase):
    pass


class BlogResponse(BlogBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class BlogUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class SearchQuery(BaseModel):
    query: Optional[str] = None
    sort_by: str = "created_at"
    order: str = "asc"
