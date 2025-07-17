from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, List
import openai
import uvicorn

# Local imports
from database import get_db, init_db
from models import User, Story
from schemas import (
    UserCreate, UserLogin, User as UserSchema, Token,
    StoryCreate, StoryUpdate, Story as StorySchema, StoryListResponse,
    StoryGenerationRequest, StoryGenerationResponse,
    MessageResponse
)
from config import settings

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="AI Story Generator API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OpenAI client setup
import openai
openai.api_key = settings.openai_api_key


# Authentication utilities
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    return user


# API Routes

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()


@app.get("/", response_model=MessageResponse)
async def root():
    """Root endpoint."""
    return {"message": f"Welcome to {settings.app_name} API"}


@app.get("/health", response_model=MessageResponse)
async def health_check():
    """Health check endpoint."""
    return {"message": "API is healthy"}


# Authentication endpoints
@app.post("/auth/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user exists
    if get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@app.post("/auth/login", response_model=Token)
async def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return access token."""
    user = authenticate_user(db, user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/auth/me", response_model=UserSchema)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user


# Story generation endpoints
@app.post("/stories/generate", response_model=StoryGenerationResponse)
async def generate_story(
    request: StoryGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a story using OpenAI API."""
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OpenAI API key not configured"
        )
    
    try:
        # Prepare the prompt
        system_prompt = "You are a creative storyteller. Generate an engaging story based on the user's prompt."
        if request.genre:
            system_prompt += f" The story should be in the {request.genre} genre."
        
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.prompt}
            ],
            max_tokens=request.max_tokens or settings.max_tokens,
            temperature=request.temperature or settings.temperature
        )
        
        generated_content = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        
        # Return the generated content
        return StoryGenerationResponse(
            id=0,  # Temporary ID for response
            prompt=request.prompt,
            generated_content=generated_content,
            model_used=settings.openai_model,
            tokens_used=tokens_used,
            generation_time=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating story: {str(e)}"
        )


# Story CRUD endpoints
@app.post("/stories", response_model=StorySchema, status_code=status.HTTP_201_CREATED)
async def create_story(
    story_data: StoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new story."""
    # For this endpoint, you might want to generate the story content
    # or allow users to provide their own content
    story = Story(
        title=story_data.title,
        prompt=story_data.prompt,
        content="",  # This could be generated or provided
        genre=story_data.genre,
        author_id=current_user.id,
        is_public=story_data.is_public
    )
    
    db.add(story)
    db.commit()
    db.refresh(story)
    
    return story


@app.get("/stories", response_model=StoryListResponse)
async def get_stories(
    skip: int = 0,
    limit: int = 20,
    public_only: bool = False,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get stories with pagination."""
    query = db.query(Story)
    
    if public_only or not current_user:
        query = query.filter(Story.is_public == True)
    else:
        # Show public stories and user's own stories
        query = query.filter(
            (Story.is_public == True) | (Story.author_id == current_user.id)
        )
    
    total = query.count()
    stories = query.offset(skip).limit(limit).all()
    
    return {
        "stories": stories,
        "total": total,
        "page": skip // limit + 1,
        "per_page": limit
    }


@app.get("/stories/{story_id}", response_model=StorySchema)
async def get_story(
    story_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific story by ID."""
    story = db.query(Story).filter(Story.id == story_id).first()
    
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found"
        )
    
    # Check if user can access this story
    if not story.is_public and (not current_user or story.author_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return story


@app.put("/stories/{story_id}", response_model=StorySchema)
async def update_story(
    story_id: int,
    story_update: StoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a story."""
    story = db.query(Story).filter(Story.id == story_id).first()
    
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found"
        )
    
    if story.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this story"
        )
    
    # Update fields
    if story_update.title is not None:
        story.title = story_update.title
    if story_update.is_public is not None:
        story.is_public = story_update.is_public
    
    db.commit()
    db.refresh(story)
    
    return story


@app.delete("/stories/{story_id}", response_model=MessageResponse)
async def delete_story(
    story_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a story."""
    story = db.query(Story).filter(Story.id == story_id).first()
    
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found"
        )
    
    if story.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this story"
        )
    
    db.delete(story)
    db.commit()
    
    return {"message": "Story deleted successfully"}


@app.get("/stories/user/me", response_model=StoryListResponse)
async def get_my_stories(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's stories."""
    query = db.query(Story).filter(Story.author_id == current_user.id)
    total = query.count()
    stories = query.offset(skip).limit(limit).all()
    
    return {
        "stories": stories,
        "total": total,
        "page": skip // limit + 1,
        "per_page": limit
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )