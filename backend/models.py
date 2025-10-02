"""Data models for blogging platform."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class UserRole(str, Enum):
    ADMIN = "admin"
    WRITER = "writer"
    READER = "reader"


class ArticleStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"


class CommentStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


# User Models
class UserBase(BaseModel):
    email: str
    name: str
    role: UserRole = UserRole.READER


class UserCreate(BaseModel):
    email: str
    password: str
    name: str


class UserLogin(BaseModel):
    email: str
    password: str


class GoogleAuthRequest(BaseModel):
    token: str


class User(UserBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    password_hash: Optional[str] = None
    google_id: Optional[str] = None
    profile_pic: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserPublic(BaseModel):
    id: str
    email: str
    name: str
    role: UserRole
    profile_pic: Optional[str] = None
    created_at: datetime


class AuthResponse(BaseModel):
    success: bool
    token: Optional[str] = None
    user: Optional[UserPublic] = None
    error: Optional[str] = None


class UpdateUserRole(BaseModel):
    role: UserRole


# Article Models
class ArticleCreate(BaseModel):
    title: str
    content: str
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    featured: Optional[bool] = None


class Article(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    author_id: str
    author_name: str
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    status: ArticleStatus = ArticleStatus.DRAFT
    likes_count: int = 0
    views_count: int = 0
    featured: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    published_at: Optional[datetime] = None


class ArticlePublic(BaseModel):
    id: str
    title: str
    content: str
    author_id: str
    author_name: str
    category: Optional[str]
    tags: List[str]
    status: ArticleStatus
    likes_count: int
    views_count: int
    featured: bool
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]


# Comment Models
class CommentCreate(BaseModel):
    article_id: str
    content: str


class Comment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    article_id: str
    user_id: str
    user_name: str
    content: str
    status: CommentStatus = CommentStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CommentPublic(BaseModel):
    id: str
    article_id: str
    user_id: str
    user_name: str
    content: str
    status: CommentStatus
    created_at: datetime


# Like Model
class Like(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    article_id: str
    user_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Settings Model
class Setting(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    key: str
    value: str


class SettingUpdate(BaseModel):
    value: str
