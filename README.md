# Intelligent Book Management System

A RESTful API for managing books with **AI-powered summaries and recommendations** using **FastAPI, PostgreSQL, and OpenAI GPT models**.

---

## Features

- **Book Management**: Add, retrieve, update, and delete books  
- **Review System**: Add and retrieve reviews for books  
- **AI-Powered Summaries**: Generate book summaries using OpenAI GPT  
- **Review Summaries**: AI-generated summaries of multiple book reviews  
- **Recommendations**: Personalized book recommendations based on preferences  
- **Authentication & Authorization**: JWT-based auth with admin-only actions  
- **Asynchronous Operations**: Fully async database and AI interactions  
- **Dockerized Setup**: Easy local and production-ready deployment  

---

## Prerequisites

- Python 3.11+
- PostgreSQL 12+
- **OpenAI API Key** with active billing
- Docker & Docker Compose (optional but recommended)

---

## Setup Instructions (Local)

### 1️⃣ Clone the Repository

```bash
git clone <repository-url>
cd jk-tech-assignment

```

### 2. Set Up Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/bookdb
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4.1-mini
SECRET_KEY=super-secret-key-change-this

```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up PostgreSQL Database

Create a PostgreSQL database:

```bash
# Using psql
createdb bookdb

# Or using SQL
psql -U postgres
CREATE DATABASE bookdb;
```

### 5. Run the Application

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

API documentation (Swagger UI) is available at `http://localhost:8000/docs`

## Docker Deployment

### Using Docker Compose (Recommended)

This will set up both PostgreSQL and the API:

```bash
docker-compose up -d
```

The API will be available at `http://localhost:8000`




## API Endpoints

### Books

- `POST /books` - Add a new book
- `GET /books` - Retrieve all books (supports query params: `skip`, `limit`, `genre`, `author`)
- `GET /books/{id}` - Retrieve a specific book by ID
- `PUT /books/{id}` - Update a book's information
- `DELETE /books/{id}` - Delete a book

### Reviews

- `POST /books/{id}/reviews` - Add a review for a book
- `GET /books/{id}/reviews` - Retrieve all reviews for a book

### Summaries and Recommendations

- `GET /books/{id}/summary` - Get book summary and aggregated rating with AI-generated review summary
- `POST /generate-summary` - Generate a summary for given book content
- `GET /recommendations` - Get book recommendations (supports query params: `user_id`, `preferred_genres`, `min_rating`)

### Utility

- `GET /` - API information
- `GET /health` - Health check endpoint

## Example Usage

### Create a Book

```bash
curl -X POST "http://localhost:8000/books" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "genre": "Fiction",
    "year_published": 1925,
    "summary": "A classic American novel about the Jazz Age"
  }'
```

### Add a Review

```bash
curl -X POST "http://localhost:8000/books/1/reviews" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "review_text": "A masterpiece of American literature!",
    "rating": 5.0
  }'
```



## Database Schema

### Books Table
- `id` (Integer, Primary Key)
- `title` (String)
- `author` (String)
- `genre` (String)
- `year_published` (Integer)
- `summary` (Text, Optional)

### Reviews Table
- `id` (Integer, Primary Key)
- `book_id` (Integer, Foreign Key to books.id)
- `user_id` (String)
- `review_text` (Text)
- `rating` (Float, 0.0-5.0)

## Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy (Async)**: Async ORM for database operations
- **AsyncPG**: Async PostgreSQL driver
- **Pydantic**: Data validation using Python type annotations
- **Docker**: Containerization for deployment


