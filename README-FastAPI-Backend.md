# AI Story Generator - FastAPI Backend

A modular FastAPI backend for an AI story generation application that integrates with OpenAI's API for story generation, uses SQLAlchemy with SQLite for data persistence, and implements JWT authentication.

## Features

- **User Authentication**: Register, login, and JWT-based authentication
- **Story Generation**: Generate stories using OpenAI's GPT models
- **Story Management**: CRUD operations for managing stories
- **Database Integration**: SQLAlchemy ORM with SQLite database
- **Data Validation**: Pydantic schemas for request/response validation
- **Modular Architecture**: Clean separation of concerns across multiple files
- **Interactive Documentation**: Automatic OpenAPI/Swagger documentation

## Project Structure

```
├── main.py              # FastAPI application and route definitions
├── config.py            # Configuration management with environment variables
├── database.py          # Database connection and session management
├── models.py            # SQLAlchemy ORM models (User, Story)
├── schemas.py           # Pydantic schemas for request/response validation
├── run_server.py        # Server startup script with database initialization
├── requirements-minimal.txt  # Python dependencies
├── .env.example         # Environment variables template
└── README-FastAPI-Backend.md  # This documentation
```

## Installation & Setup

### 1. Create Virtual Environment

```bash
python3 -m venv fastapi_env
source fastapi_env/bin/activate  # On Windows: fastapi_env\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements-minimal.txt
```

### 3. Environment Configuration

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` file with your configuration:

```env
# App Configuration
APP_NAME="AI Story Generator"
DEBUG=False
HOST=0.0.0.0
PORT=8000

# Database Configuration
DATABASE_URL=sqlite:///./stories.db

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
MAX_TOKENS=1000
TEMPERATURE=0.7

# Security Configuration
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 4. Run the Server

```bash
python run_server.py
```

The server will start at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:

- **Interactive API Documentation**: http://localhost:8000/docs
- **Alternative API Documentation**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login and get access token |
| GET | `/auth/me` | Get current user info |

### Stories

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/stories/generate` | Generate a story using AI |
| POST | `/stories` | Create a new story |
| GET | `/stories` | List all stories (paginated) |
| GET | `/stories/{id}` | Get specific story |
| PUT | `/stories/{id}` | Update a story |
| DELETE | `/stories/{id}` | Delete a story |
| GET | `/stories/user/me` | Get current user's stories |

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint |
| GET | `/health` | Health check |

## Usage Examples

### 1. Register a User

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "storyteller",
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "storyteller",
    "password": "securepassword123"
  }'
```

### 3. Generate a Story

```bash
curl -X POST http://localhost:8000/stories/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "prompt": "A brave knight embarks on a quest to save a dragon from a princess",
    "genre": "fantasy",
    "max_tokens": 500,
    "temperature": 0.8
  }'
```

### 4. Create a Story

```bash
curl -X POST http://localhost:8000/stories \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "title": "The Dragon Quest",
    "prompt": "A brave knight embarks on a quest",
    "content": "Once upon a time, in a land far away...",
    "genre": "fantasy",
    "is_public": true
  }'
```

### 5. List Stories

```bash
curl -X GET http://localhost:8000/stories \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Database Schema

### Users Table
- `id`: Primary key
- `username`: Unique username
- `email`: Unique email address
- `hashed_password`: Bcrypt hashed password
- `is_active`: Account status
- `created_at`: Account creation timestamp
- `updated_at`: Last update timestamp

### Stories Table
- `id`: Primary key
- `title`: Story title
- `prompt`: User prompt for story generation
- `content`: Story content
- `genre`: Story genre (optional)
- `is_public`: Public visibility flag
- `author_id`: Foreign key to users table
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

## Configuration Options

The application supports configuration through environment variables:

### App Settings
- `APP_NAME`: Application name (default: "AI Story Generator")
- `DEBUG`: Debug mode (default: False)
- `HOST`: Server host (default: "0.0.0.0")
- `PORT`: Server port (default: 8000)

### Database Settings
- `DATABASE_URL`: SQLite database URL (default: "sqlite:///./stories.db")

### OpenAI Settings
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_MODEL`: Model to use (default: "gpt-3.5-turbo")
- `MAX_TOKENS`: Maximum tokens per generation (default: 1000)
- `TEMPERATURE`: Creativity level 0.0-1.0 (default: 0.7)

### Security Settings
- `SECRET_KEY`: JWT secret key
- `ALGORITHM`: JWT algorithm (default: "HS256")
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: 30)

## Development

### Project Architecture

The backend follows a modular architecture with clear separation of concerns:

1. **main.py**: FastAPI application setup, middleware, and route definitions
2. **config.py**: Configuration management using Pydantic settings
3. **database.py**: SQLAlchemy engine, session management, and database utilities
4. **models.py**: SQLAlchemy ORM models defining database tables
5. **schemas.py**: Pydantic models for request/response validation and serialization

### Authentication Flow

1. User registers with username, email, and password
2. Password is hashed using bcrypt
3. User logs in to receive a JWT access token
4. Token is included in Authorization header for protected endpoints
5. Token contains user information and expiration time

### Story Generation Flow

1. User sends a prompt with optional parameters (genre, max_tokens, temperature)
2. System constructs a prompt for the AI model
3. OpenAI API is called with the constructed prompt
4. Generated story is returned to the user
5. Optionally, the story can be saved to the database

## Error Handling

The API returns standard HTTP status codes:

- **200**: Success
- **201**: Created
- **400**: Bad Request (validation errors)
- **401**: Unauthorized (invalid/missing token)
- **404**: Not Found
- **422**: Unprocessable Entity (validation errors)
- **500**: Internal Server Error

## Security Considerations

- Passwords are hashed using bcrypt
- JWT tokens have configurable expiration times
- API endpoints are protected with authentication
- Input validation using Pydantic schemas
- CORS middleware configured (adjust for production)

## Production Deployment

For production deployment, consider:

1. Use a production ASGI server like Gunicorn with Uvicorn workers
2. Set up a reverse proxy (Nginx)
3. Use a production database (PostgreSQL, MySQL)
4. Configure proper environment variables
5. Set up SSL/TLS certificates
6. Implement proper logging and monitoring
7. Use Docker for containerization

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed in the virtual environment
2. **Database Errors**: Check if the database file has proper permissions
3. **OpenAI Errors**: Verify your API key is valid and has sufficient credits
4. **Authentication Errors**: Check JWT secret key configuration

### Debug Mode

Enable debug mode by setting `DEBUG=True` in your environment variables for detailed error messages.

## License

This project is provided as-is for educational and development purposes.