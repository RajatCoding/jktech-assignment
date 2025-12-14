from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str
    is_admin: bool = False  # Default to False, only admins can set this to True


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class BookBase(BaseModel):
    title: str
    author: str
    genre: str
    year_published: int = Field(..., ge=1000, le=9999)
    summary: Optional[str] = None


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    genre: Optional[str] = None
    year_published: Optional[int] = Field(None, ge=1000, le=9999)
    summary: Optional[str] = None


class BookResponse(BookBase):
    id: int
    
    class Config:
        from_attributes = True


class ReviewBase(BaseModel):
    review_text: str
    rating: float = Field(..., ge=0.0, le=5.0)


class ReviewCreate(ReviewBase):
    # user_id is automatically set from authenticated user
    pass


class ReviewResponse(ReviewBase):
    id: int
    book_id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class BookSummaryResponse(BaseModel):
    book_id: int
    title: str
    author: str
    summary: Optional[str]
    average_rating: float
    total_reviews: int
    review_summary: Optional[str] = None


class GenerateSummaryRequest(BaseModel):
    content: str
    book_title: Optional[str] = None
    author: Optional[str] = None


class GenerateSummaryResponse(BaseModel):
    summary: str


class RecommendationRequest(BaseModel):
    user_id: Optional[str] = None
    preferred_genres: Optional[List[str]] = None
    min_rating: Optional[float] = Field(None, ge=0.0, le=5.0)


class RecommendationResponse(BaseModel):
    recommendations: List[BookResponse]
    reason: str


