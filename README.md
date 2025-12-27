# Intelligent Book Management System

A RESTful API for managing books with **AI-powered summaries and recommendations** using **FastAPI, PostgreSQL, and AI models** (OpenRouter/OpenAI compatible).

---

## Features

- **Book Management**: Add, retrieve, update, and delete books (Admin only for create/delete)
- **Review System**: Add and retrieve reviews for books (Authenticated users)
- **AI-Powered Summaries**: Generate book summaries using AI models (GPT-4o-mini, Llama-3, etc.)
- **Review Summaries**: AI-generated summaries of multiple book reviews
- **Recommendations**: Personalized book recommendations based on user preferences
- **Authentication & Authorization**: JWT-based authentication with role-based access control
  - **Admin Users**: Can create and delete books
  - **Normal Users**: Can create reviews and view books
- **Asynchronous Operations**: Fully async database and AI interactions
- **Dockerized Setup**: Easy local and production-ready deployment
- **Comprehensive Test Suite**: Unit tests with pytest

---

## Prerequisites

- **Python 3.11+**
- **PostgreSQL 12+**
- **AI Model API Key** (OpenRouter API key)
- **Docker & Docker Compose** (optional but recommended)

---

## Setup Instructions

### Option 1: Docker Compose (Recommended)

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd jk-tech-assignment
   ```

2. **Create `.env` file:**
   ```env
   DATABASE_URL=postgresql+asyncpg://bookuser:bookpass@db:5432/bookdb
   OPEN_ROUTER_API_KEY=your-openrouter-api-key
   LLM_MODEL=meta-llama/llama-3-8b-instruct
   # OPEN_ROUTER_API_KEY=your-aopenrouter-api-key
   # LLM_MODEL=meta-llama/llama-3-8b-instruct
   # LLM_BASE_URL=https://openrouter.ai/api/v1
   SECRET_KEY=your-secret-key-change-this-in-production
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

3. **Start services:**
   ```bash
   docker-compose up -d
   ```

4. **Access the API:**
   - API: `http://localhost:8000`
   - Interactive Docs: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

### Option 2: Local Development

1. **Clone and navigate:**
   ```bash
   git clone <repository-url>
   cd jk-tech-assignment
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL:**
   ```bash
   # Create database
   createdb bookdb
   
   # Or using psql
   psql -U postgres
   CREATE DATABASE bookdb;
   \q
   ```

5. **Create `.env` file:**
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/bookdb
   OPEN_ROUTER_API_KEY=your-api-key-here
   LLM_MODEL=meta-llama/llama-3-8b-instruct
   LLM_BASE_URL=https://openrouter.ai/api/v1
   
   SECRET_KEY=your-secret-key-change-this
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

6. **Run the application:**
   ```bash
   uvicorn main:app --reload
   ```

---

## Authentication

### Register a User

```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "password": "securepassword123",
    "is_admin": false
  }'
```

### Register an Admin

```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "adminpass123",
    "is_admin": true
  }'
```

### Login

```bash
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john_doe&password=securepassword123"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Use Token

Include the token in subsequent requests:
```bash
curl -X GET "http://localhost:8000/users/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/register` | Register a new user | No |
| `POST` | `/login` | Login and get JWT token | No |
| `GET` | `/users/me` | Get current user info | Yes |

### Books

| Method | Endpoint | Description | Auth Required | Role |
|--------|----------|-------------|---------------|------|
| `POST` | `/books` | Create a new book | Yes | **Admin** |
| `GET` | `/books` | List all books (with filters) | No | - |
| `GET` | `/books/{id}` | Get book by ID | No | - |
| `PUT` | `/books/{id}` | Update book | No | - |
| `DELETE` | `/books/{id}` | Delete book | Yes | **Admin** |

**Query Parameters for `GET /books`:**
- `skip` (int): Pagination offset (default: 0)
- `limit` (int): Results per page (default: 100)
- `genre` (string): Filter by genre
- `author` (string): Filter by author

### Reviews

| Method | Endpoint | Description | Auth Required | Role |
|--------|----------|-------------|---------------|------|
| `POST` | `/books/{id}/reviews` | Add a review | Yes | User/Admin |
| `GET` | `/books/{id}/reviews` | Get all reviews for a book | No | - |

### AI Features

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/books/{id}/summary` | Get book summary with AI-generated review summary | No |
| `POST` | `/generate-summary` | Generate summary for book content | No |
| `GET` | `/recommendations` | Get personalized recommendations | No |

**Query Parameters for `GET /recommendations`:**
- `user_id` (int): User ID to exclude reviewed books
- `preferred_genres` (string): Comma-separated genres (e.g., "Fiction,Science Fiction")
- `min_rating` (float): Minimum average rating (0.0-5.0)

### Utility

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API information |
| `GET` | `/health` | Health check |

---

## Example Usage

### 1. Register and Login

```bash
# Register
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "email": "alice@example.com",
    "password": "alice123"
  }'

# Login
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice&password=alice123"

# Save token
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 2. Create a Book (Admin Only)

```bash
curl -X POST "http://localhost:8000/books" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "1984",
    "author": "George Orwell",
    "genre": "Fiction",
    "year_published": 1949,
    "summary": "A dystopian novel about totalitarianism"
  }'
```

### 3. Add a Review (Any Authenticated User)

```bash
curl -X POST "http://localhost:8000/books/1/reviews" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "review_text": "A thought-provoking masterpiece!",
    "rating": 5.0
  }'
```

### 4. Get Book Summary with AI-Generated Review Summary

```bash
curl "http://localhost:8000/books/1/summary"
```

**Response:**
```json
{
  "book_id": 1,
  "title": "1984",
  "author": "George Orwell",
  "summary": "A dystopian novel...",
  "average_rating": 4.5,
  "total_reviews": 10,
  "review_summary": "Reviews are overwhelmingly positive, praising the novel's relevance and thought-provoking themes..."
}
```

### 5. Generate Summary

```bash
curl -X POST "http://localhost:8000/generate-summary" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "A young wizard discovers his magical abilities...",
    "book_title": "Harry Potter",
    "author": "J.K. Rowling"
  }'
```

### 6. Get Recommendations

```bash
curl "http://localhost:8000/recommendations?preferred_genres=Fiction&min_rating=4.0&user_id=1"
```

---

## Database Schema

### Users Table
- `id` (Integer, Primary Key)
- `username` (String, Unique)
- `email` (String, Unique)
- `full_name` (String, Optional)
- `hashed_password` (String)
- `is_active` (String, default: "true")
- `is_admin` (Boolean, default: false)
- `created_at` (DateTime)

### Books Table
- `id` (Integer, Primary Key)
- `title` (String)
- `author` (String)
- `genre` (String)
- `year_published` (Integer)
- `summary` (Text, Optional)

### Reviews Table
- `id` (Integer, Primary Key)
- `book_id` (Integer, Foreign Key → books.id)
- `user_id` (Integer, Foreign Key → users.id)
- `review_text` (Text)
- `rating` (Float, 0.0-5.0)
- `created_at` (DateTime)

---

## AI Model Configuration

### Using OpenRouter (Default)

The system uses **OpenRouter** which provides access to multiple AI models including:
- `meta-llama/llama-3-8b-instruct` (default)
- `openai/gpt-4o-mini`
- `openai/gpt-4o`
- `anthropic/claude-3-haiku`
- And many more...

**Setup:**
1. Get API key from [OpenRouter.ai](https://openrouter.ai)
2. Set in `.env`:
   ```env
   OPEN_ROUTER_API_KEY=your-key-here
   LLM_MODEL=meta-llama/llama-3-8b-instruct
   LLM_BASE_URL=https://openrouter.ai/api/v1
   ```

### Using OpenAI Directly

To use OpenAI directly:

```env
OPEN_ROUTER_API_KEY=sk-your-openai-key
LLM_MODEL=gpt-4o-mini
LLM_BASE_URL=https://api.openai.com/v1
```

### Using Azure OpenAI

```env
OPEN_ROUTER_API_KEY=your-azure-key
LLM_MODEL=your-deployment-name
LLM_BASE_URL=https://your-resource.openai.azure.com/v1
```

---

## Testing

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=. --cov-report=html
```

### Run Specific Test File

```bash
pytest tests/test_auth.py -v
pytest tests/test_books.py -v
pytest tests/test_reviews.py -v
```

### Test Coverage

- Authentication (registration, login, tokens)
- Book CRUD operations
- Review creation and retrieval
- Admin vs User permissions
- AI service mocking
- Recommendations logic

---

## Security Features

- **Password Hashing**: Bcrypt with SHA-256 pre-hashing
- **JWT Tokens**: Secure token-based authentication
- **Token Expiration**: Configurable token expiry (default: 30 minutes)
- **Role-Based Access Control**: Admin and user roles
- **Input Validation**: Pydantic schema validation
- **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries

---

## Project Structure

```
jk-tech-assignment/
├── main.py                 # FastAPI application and endpoints
├── models.py               # SQLAlchemy database models
├── schemas.py              # Pydantic request/response schemas
├── database.py             # Database connection and session management
├── auth.py                 # Authentication and authorization logic
├── llama_service.py        # AI model service (OpenRouter/OpenAI)
├── config.py               # Configuration management
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker image configuration
├── docker-compose.yml      # Docker Compose setup
├── pytest.ini              # Pytest configuration
├── tests/                  # Test suite
│   ├── conftest.py         # Test fixtures
│   ├── test_auth.py        # Authentication tests
│   ├── test_books.py       # Book CRUD tests
│   ├── test_reviews.py     # Review tests
│   ├── test_recommendations.py  # Recommendation tests
│   └── test_llama_service.py    # AI service tests
├── example_usage.py        # Example API usage script
├── README.md               # This file
├── FASTAPI_GUIDE.md        # FastAPI learning guide
└── GPT_SETUP.md            # AI model setup guide
```

---

## Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy (Async)**: Async ORM for database operations
- **AsyncPG**: Async PostgreSQL driver
- **Pydantic**: Data validation using Python type annotations
- **JWT (python-jose)**: Token-based authentication
- **Bcrypt (passlib)**: Password hashing
- **HTTPX**: Async HTTP client for AI API calls
- **Pytest**: Testing framework
- **Docker**: Containerization
- **PostgreSQL**: Relational database

---

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | - |
| `OPEN_ROUTER_API_KEY` | OpenRouter/OpenAI API key | Yes | - |
| `LLM_MODEL` | AI model name | No | `meta-llama/llama-3-8b-instruct` |
| `LLM_BASE_URL` | AI API base URL | No | `https://openrouter.ai/api/v1` |
| `SECRET_KEY` | JWT secret key | Yes | - |
| `ALGORITHM` | JWT algorithm | No | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry time | No | `30` |

---

## Deployment

### Docker Deployment

The application is containerized and ready for deployment:

```bash
docker-compose up -d
```

### Cloud Deployment Options

- **AWS ECS/Fargate**: Use Dockerfile with ECS task definitions
- **Google Cloud Run**: Deploy container directly
- **Azure Container Instances**: Use Docker image
- **Heroku**: Use Dockerfile with Heroku container registry
- **DigitalOcean App Platform**: Deploy using Docker

**Production Checklist:**
- Use managed PostgreSQL database
- Set strong `SECRET_KEY` in environment
- Enable HTTPS/TLS
- Configure proper CORS settings
- Set up monitoring and logging
- Use environment-specific API keys

---

## Additional Documentation

- **[FASTAPI_GUIDE.md](FASTAPI_GUIDE.md)**: Comprehensive FastAPI learning guide
- **[GPT_SETUP.md](GPT_SETUP.md)**: AI model configuration guide

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

MIT License

---

## Troubleshooting

### Database Connection Issues

- Verify PostgreSQL is running: `pg_isready`
- Check connection string format: `postgresql+asyncpg://user:pass@host:port/db`
- Ensure database exists: `createdb bookdb`

### Authentication Issues

- Verify `SECRET_KEY` is set in `.env`
- Check token expiration time
- Ensure user is active (`is_active="true"`)

### AI Model Issues

- Verify API key is valid
- Check API key has sufficient credits/quota
- Verify model name is correct
- Check network connectivity

### Test Failures

- Ensure test database is set up (uses SQLite in-memory)
- Run `pytest -v` for detailed output
- Check that all dependencies are installed

---

## Support

For issues and questions, please open an issue on GitHub.

---

**Built with FastAPI, PostgreSQL, and AI**
