from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# Base schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    username: str
    password: str


class UserInDB(UserBase):
    class Config:
        from_attributes = True
    
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class User(UserInDB):
    pass


# Story schemas
class StoryBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    prompt: str = Field(..., min_length=10, max_length=2000)
    genre: Optional[str] = Field(None, max_length=50)
    is_public: bool = False


class StoryCreate(StoryBase):
    pass


class StoryUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    is_public: Optional[bool] = None


class StoryInDB(StoryBase):
    class Config:
        from_attributes = True
    
    id: int
    content: str
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class Story(StoryInDB):
    author: Optional[User] = None


# Story generation schemas
class StoryGenerationRequest(BaseModel):
    prompt: str = Field(..., min_length=10, max_length=2000)
    genre: Optional[str] = Field(None, max_length=50)
    max_tokens: Optional[int] = Field(1000, ge=100, le=2000)
    temperature: Optional[float] = Field(0.7, ge=0.0, le=1.0)


class StoryGenerationResponse(BaseModel):
    class Config:
        from_attributes = True
    
    id: int
    prompt: str
    generated_content: str
    model_used: str
    tokens_used: Optional[int] = None
    generation_time: datetime


# Response schemas
class StoryListResponse(BaseModel):
    stories: List[Story]
    total: int
    page: int
    per_page: int


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# Error schemas
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None


class MessageResponse(BaseModel):
    message: str