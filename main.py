from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
from datetime import timedelta
import logging

from database import get_db, engine, Base
from models import Book, Review, User
from schemas import (
    BookCreate, BookUpdate, BookResponse,
    ReviewCreate, ReviewResponse,
    BookSummaryResponse, GenerateSummaryRequest,
    GenerateSummaryResponse, RecommendationRequest,
    RecommendationResponse, UserCreate, UserResponse,
    Token, UserLogin
)
from llama_service import llama_service
from auth import (
    get_password_hash, authenticate_user, create_access_token,
    get_current_active_user, get_current_admin_user, ACCESS_TOKEN_EXPIRE_MINUTES
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Intelligent Book Management System",
    description="A RESTful API for managing books with AI-powered summaries and recommendations",
    version="1.0.0"
)


@app.on_event("startup")
async def startup():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")


@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()
    logger.info("Database connection closed")


# Authentication endpoints
@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    # Check if username already exists
    result = await db.execute(select(User).where(User.username == user.username))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user.email))
    existing_email = result.scalar_one_or_none()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user with hashed password
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        is_active="true",
        is_admin=user.is_admin  # Set admin status from request
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@app.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Login and get access token."""
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return current_user


# Book endpoints
@app.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    book: BookCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a new book to the database (Admin only)."""
    db_book = Book(**book.model_dump())
    db.add(db_book)
    await db.commit()
    await db.refresh(db_book)
    return db_book


@app.get("/books", response_model=List[BookResponse])
async def get_books(
    skip: int = 0,
    limit: int = 100,
    genre: Optional[str] = None,
    author: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve all books with optional filtering."""
    query = select(Book)
    
    if genre:
        query = query.where(Book.genre.ilike(f"%{genre}%"))
    if author:
        query = query.where(Book.author.ilike(f"%{author}%"))
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    books = result.scalars().all()
    return books


@app.get("/books/{book_id}", response_model=BookResponse)
async def get_book(book_id: int, db: AsyncSession = Depends(get_db)):
    """Retrieve a specific book by its ID."""
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    return book


@app.put("/books/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: int,
    book_update: BookUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a book's information by its ID."""
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    
    update_data = book_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(book, field, value)
    
    await db.commit()
    await db.refresh(book)
    return book


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a book by its ID (Admin only)."""
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    
    await db.delete(book)
    await db.commit()
    return None


# Review endpoints
@app.post("/books/{book_id}/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    book_id: int,
    review: ReviewCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a review for a book (requires authentication)."""
    # Check if book exists
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    
    # Use current authenticated user's ID instead of review.user_id
    # This ensures users can only create reviews for themselves
    db_review = Review(
        book_id=book_id,
        user_id=current_user.id,  # Use authenticated user's ID
        review_text=review.review_text,
        rating=review.rating
    )
    db.add(db_review)
    await db.commit()
    await db.refresh(db_review)
    return db_review


@app.get("/books/{book_id}/reviews", response_model=List[ReviewResponse])
async def get_reviews(
    book_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve all reviews for a book."""
    # Check if book exists
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    
    result = await db.execute(select(Review).where(Review.book_id == book_id))
    reviews = result.scalars().all()
    return reviews


@app.get("/books/{book_id}/summary", response_model=BookSummaryResponse)
async def get_book_summary(book_id: int, db: AsyncSession = Depends(get_db)):
    """Get a summary and aggregated rating for a book."""
    # Get book
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    
    # Get reviews and calculate average rating
    result = await db.execute(select(Review).where(Review.book_id == book_id))
    reviews = result.scalars().all()
    
    if reviews:
        avg_rating = sum(r.rating for r in reviews) / len(reviews)
        # Generate review summary using Llama3
        try:
            reviews_data = [
                {"rating": r.rating, "review_text": r.review_text}
                for r in reviews
            ]
            review_summary = await llama_service.generate_review_summary(reviews_data)
        except Exception as e:
            logger.error(f"Error generating review summary: {e}")
            review_summary = None
    else:
        avg_rating = 0.0
        review_summary = None
    
    return BookSummaryResponse(
        book_id=book.id,
        title=book.title,
        author=book.author,
        summary=book.summary,
        average_rating=round(avg_rating, 2),
        total_reviews=len(reviews),
        review_summary=review_summary
    )


@app.post("/generate-summary", response_model=GenerateSummaryResponse)
async def generate_summary(request: GenerateSummaryRequest):
    """Generate a summary for given book content using Llama3."""
    try:
        summary = await llama_service.generate_summary(
            request.content,
            request.book_title,
            request.author
        )
        return GenerateSummaryResponse(summary=summary)
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate summary: {str(e)}"
        )


@app.get("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(
    user_id: Optional[str] = None,
    preferred_genres: Optional[str] = None,
    min_rating: Optional[float] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get book recommendations based on user preferences."""
    query = select(Book)
    conditions = []
    
    # Filter by preferred genres
    if preferred_genres:
        genres_list = [g.strip() for g in preferred_genres.split(",")]
        genre_conditions = [Book.genre.ilike(f"%{genre}%") for genre in genres_list]
        if genre_conditions:
            conditions.append(or_(*genre_conditions))
    
    # Filter by minimum rating
    if min_rating is not None:
        # Subquery to get books with average rating >= min_rating
        subquery = (
            select(Review.book_id, func.avg(Review.rating).label("avg_rating"))
            .group_by(Review.book_id)
            .having(func.avg(Review.rating) >= min_rating)
            .subquery()
        )
        conditions.append(Book.id.in_(select(subquery.c.book_id)))
    
    # If user_id provided, prioritize books they haven't reviewed
    if user_id:
        # Convert string user_id to int if needed (for backward compatibility)
        try:
            user_id_int = int(user_id) if isinstance(user_id, str) else user_id
            user_reviewed_books = select(Review.book_id).where(Review.user_id == user_id_int)
            conditions.append(~Book.id.in_(user_reviewed_books))
        except (ValueError, TypeError):
            # If user_id is not a valid integer, skip this filter
            pass
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Order by average rating (join with reviews to get avg rating)
    avg_rating_subq = (
        select(Review.book_id, func.avg(Review.rating).label("avg_rating"))
        .group_by(Review.book_id)
        .subquery()
    )
    
    query = query.outerjoin(avg_rating_subq, Book.id == avg_rating_subq.c.book_id)
    query = query.order_by(
        func.coalesce(avg_rating_subq.c.avg_rating, 0).desc(),
        Book.id.desc()
    )
    query = query.limit(10)
    
    result = await db.execute(query)
    books = result.scalars().all()
    
    if not books:
        # Fallback: return top-rated books
        avg_rating_fallback = (
            select(Review.book_id, func.avg(Review.rating).label("avg_rating"))
            .group_by(Review.book_id)
            .subquery()
        )
        result = await db.execute(
            select(Book)
            .outerjoin(avg_rating_fallback, Book.id == avg_rating_fallback.c.book_id)
            .order_by(
                func.coalesce(avg_rating_fallback.c.avg_rating, 0).desc(),
                Book.id.desc()
            )
            .limit(10)
        )
        books = result.scalars().all()
        reason = "Showing popular books as no specific recommendations found."
    else:
        genre_text = preferred_genres if preferred_genres else "all genres"
        rating_text = f" with rating >= {min_rating}" if min_rating else ""
        reason = f"Recommended based on your preferences: {genre_text}{rating_text}"
    
    return RecommendationResponse(
        recommendations=books,
        reason=reason
    )


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Intelligent Book Management System API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

