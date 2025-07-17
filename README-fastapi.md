# AI Story Generator - FastAPI Backend

A modular FastAPI backend for an AI story generation application that integrates with OpenAI's API for story generation, uses SQLAlchemy with SQLite for data persistence, and implements JWT authentication.

## Features

- **User Authentication**: Register, login, and JWT-based authentication
- **Story Generation**: Generate stories using OpenAI's GPT models
- **Story Management**: CRUD operations for managing stories
- **Database Integration**: SQLAlchemy ORM with SQLite database
- **Data Validation**: Pydantic schemas for request/response validation
- **Modular Architecture**: Clean separation of concerns across multiple files

## Project Structure

```
├── main.py          # FastAPI application and route definitions
├── config.py        # Configuration management with Pydantic Settings
├── database.py      # Database connection and session management
├── models.py        # SQLAlchemy database models
├── schemas.py       # Pydantic schemas for validation
├── requirements-fastapi.txt  # Python dependencies
├── .env.example     # Environment variables example
└── README-fastapi.md # This file
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements-fastapi.txt
```

### 2. Environment Configuration

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` and set your OpenAI API key:

```env
OPENAI_API_KEY=your_actual_openai_api_key_here
SECRET_KEY=your-super-secret-key-for-jwt
```

### 3. Initialize Database

The database will be automatically initialized when you start the application. Alternatively, you can initialize it manually:

```bash
python database.py
```

### 4. Run the Application

```bash
# Development mode with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or using Python directly
python main.py
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:

- **Interactive API docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative API docs (ReDoc)**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## API Endpoints

### Authentication

- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get access token
- `GET /auth/me` - Get current user information

### Story Generation

- `POST /stories/generate` - Generate a story using OpenAI API

### Story Management

- `POST /stories` - Create a new story
- `GET /stories` - Get stories with pagination
- `GET /stories/{story_id}` - Get a specific story
- `PUT /stories/{story_id}` - Update a story
- `DELETE /stories/{story_id}` - Delete a story
- `GET /stories/user/me` - Get current user's stories

### Health Check

- `GET /` - Root endpoint
- `GET /health` - Health check endpoint

## Usage Examples

### 1. Register a User

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "storyteller",
    "email": "user@example.com",
    "password": "secretpassword"
  }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "storyteller",
    "password": "secretpassword"
  }'
```

### 3. Generate a Story

```bash
curl -X POST "http://localhost:8000/stories/generate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "prompt": "A brave knight on a quest to save a dragon from a princess",
    "genre": "fantasy",
    "max_tokens": 500,
    "temperature": 0.8
  }'
```

### 4. Get Stories

```bash
curl -X GET "http://localhost:8000/stories?skip=0&limit=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Configuration Options

All configuration can be set via environment variables or the `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Application name | "AI Story Generator" |
| `DEBUG` | Enable debug mode | False |
| `HOST` | Server host | "0.0.0.0" |
| `PORT` | Server port | 8000 |
| `DATABASE_URL` | SQLite database URL | "sqlite:///./stories.db" |
| `OPENAI_API_KEY` | OpenAI API key | "" |
| `OPENAI_MODEL` | OpenAI model to use | "gpt-3.5-turbo" |
| `MAX_TOKENS` | Default max tokens for generation | 1000 |
| `TEMPERATURE` | Default temperature for generation | 0.7 |
| `SECRET_KEY` | JWT secret key | "your-super-secret-key-change-in-production" |
| `ALGORITHM` | JWT algorithm | "HS256" |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | 30 |

## Database Schema

### Users Table
- `id` (Primary Key)
- `username` (Unique)
- `email` (Unique)
- `hashed_password`
- `is_active`
- `created_at`
- `updated_at`

### Stories Table
- `id` (Primary Key)
- `title`
- `prompt`
- `content`
- `genre`
- `author_id` (Foreign Key)
- `is_public`
- `created_at`
- `updated_at`

### Story Generations Table
- `id` (Primary Key)
- `prompt`
- `generated_content`
- `model_used`
- `tokens_used`
- `generation_time`
- `user_id` (Foreign Key)

## Security Features

- Password hashing using bcrypt
- JWT token-based authentication
- Protected routes requiring authentication
- Input validation using Pydantic
- CORS middleware for cross-origin requests

## Development

### Running Tests

```bash
pytest
```

### Code Structure

The application follows a modular architecture:

- **main.py**: FastAPI app instance, middleware, and route definitions
- **config.py**: Centralized configuration using Pydantic Settings
- **database.py**: Database engine, session management, and initialization
- **models.py**: SQLAlchemy ORM models
- **schemas.py**: Pydantic models for request/response validation

## Production Deployment

For production deployment:

1. Set `DEBUG=False` in your environment
2. Use a proper secret key
3. Configure CORS origins appropriately
4. Consider using PostgreSQL instead of SQLite
5. Use a production ASGI server like Gunicorn with Uvicorn workers
6. Set up proper logging and monitoring

## License

This project is open source and available under the MIT License.