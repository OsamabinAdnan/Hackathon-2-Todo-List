# Backend Development Rules - Hackathon II Todo App Full-Stack Web App

This file provides backend-specific development guidance for Claude Code working on the FastAPI application for the Hackathon II Todo Application project.

You are an expert backend developer specializing in FastAPI, SQLModel, and async Python. Your primary goal is to generate secure, performant, type-safe backend code following Spec-Driven Development principles.

**Parent Guidelines**: See `../CLAUDE.md` for root-level SDD workflow
**Constitution**: See `../.specify/memory/constitution.md` for project principles

---

## Phase 2: Backend Development (Full-Stack Web Application)

This is the **FastAPI** backend for the Hackathon II Phase 2 Todo application with multi-user authentication and PostgreSQL persistence. This is Phase 2 of 5 (Full-Stack Web Application)

### Phase 2 Technology Stack
- **Language**: Python 3.13+
- **Package Manager**: UV Package Manager
- **Framework**: FastAPI (async web framework)
- **ORM**: SQLModel (combines SQLAlchemy + Pydantic)
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: Better Auth (JWT token generation/validation)
- **Package Manager**: UV (fast Python package manager)
- **Testing**: pytest + httpx (async testing)
- **Linting**: Ruff (linter + formatter)

### Referencing Specs for Backend Implementation

When implementing backend features, ALWAYS reference the relevant specification files to understand business logic, API contracts, and database schema.

**Backend Implementation Examples:**
```
# Implement API endpoint
User: @specs/api/rest-endpoints.md implement POST /api/{user_id}/tasks endpoint

# Implement database model
User: @specs/database/schema.md implement the Task SQLModel with all constraints

# Implement authentication
User: @specs/features/authentication.md implement JWT token generation and verification middleware

# Implement business logic
User: @specs/features/task-crud.md implement recurring task auto-reschedule logic
```

**Key Specs for Backend:**
- `@specs/api/rest-endpoints.md` - Complete API contracts (routes, request/response, errors)
- `@specs/database/schema.md` - Database schema, SQLModel definitions, indexes
- `@specs/features/authentication.md` - JWT implementation, password hashing, user isolation
- `@specs/features/task-crud.md` - Business logic, validation rules, edge cases

**Before Writing Backend Code:**
1. Read the API spec for endpoint contract (request/response/errors)
2. Read the database schema for model definitions and constraints
3. Read the feature spec for business logic and validation rules
4. **Write tests FIRST** (TDD - Red-Green-Refactor)
5. Implement with proper type hints, error handling, and security checks

### TDD for Backend (MANDATORY)

**Test-First Development:**
```
# Example: Implement user signup endpoint

# Step 1: Write failing test
User: @specs/testing/backend-testing.md implement test for POST /api/auth/signup endpoint

# Step 2: Run test (should FAIL - Red)
User: pytest tests/test_auth.py::test_signup_creates_user

# Step 3: Implement minimal code
User: @specs/api/rest-endpoints.md implement POST /api/auth/signup endpoint

# Step 4: Run test (should PASS - Green)
User: pytest tests/test_auth.py::test_signup_creates_user

# Step 5: Refactor for better code organization
User: Extract password hashing logic into separate utility function

# Step 6: Run all tests (should still PASS)
User: pytest
```

**Testing Stack:**
- **pytest**: Test framework
- **httpx**: Async HTTP client for API testing
- **pytest-cov**: Coverage reporting
- **SQLite (in-memory)**: Fast unit tests
- **PostgreSQL**: Integration tests

**Coverage Requirements:**
- 80%+ overall coverage
- 100% for authentication logic
- 100% for security-related code (user isolation, JWT)
- 100% for recurring task logic

**Security Tests (MANDATORY):**
- User isolation tests (cross-user access attempts)
- SQL injection prevention tests
- XSS prevention tests
- JWT expiry and tampering tests

**Test Specifications:** `@specs/testing/backend-testing.md`

### Backend Context

This is the **FastAPI** backend for the Hackathon II Phase 2 Todo application with multi-user authentication and PostgreSQL persistence.

### Technology Stack
- **Language**: Python 3.13+
- **Package Manager**: UV Package Manager
- **Framework**: FastAPI (async web framework)
- **ORM**: SQLModel (combines SQLAlchemy + Pydantic)
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: Better Auth (JWT token generation/validation)
- **Package Manager**: UV (fast Python package manager)
- **Testing**: pytest + httpx (async testing)
- **Linting**: Ruff (linter + formatter)

---

### Project Structure

```
backend/
├── app/
│   ├── .python-version        # Python version specification
├   |── CLAUDE.md              # Backend development guidelines
│   ├── main.py                # FastAPI application entry point
│   ├── config.py              # Environment variables and settings
│   ├── database.py            # Database connection and session management
│   ├── models/                # SQLModel database models
│   │   ├── __init__.py
│   │   ├── user.py           # User model
│   │   └── task.py           # Task model
│   ├── schemas/               # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── user.py           # User DTOs
│   │   └── task.py           # Task DTOs
│   ├── routes/                # API endpoint routers
│   │   ├── __init__.py
│   │   ├── auth.py           # /api/auth/* endpoints
│   │   └── tasks.py          # /api/{user_id}/tasks/* endpoints
│   ├── services/              # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py   # Authentication logic
│   │   └── task_service.py   # Task CRUD logic
│   ├── middleware/            # Custom middleware
│   │   ├── __init__.py
│   │   ├── auth.py           # JWT verification middleware
│   │   └── cors.py           # CORS configuration
│   └── utils/                 # Utility functions
│       ├── __init__.py
│       ├── jwt.py            # JWT token utilities
│       └── security.py       # Password hashing utilities
├── tests/
│   ├── test_auth.py          # Auth endpoint tests
│   ├── test_tasks.py         # Task endpoint tests
│   └── conftest.py           # Pytest fixtures
├── migrations/                # Database migrations (Alembic)
│   └── versions/
├── pyproject.toml             # UV/Poetry dependencies
├── .env                       # Environment variable
├── README.md
└── uv.lock                    # Locked dependency versions
```

---

### FastAPI Application Setup

#### Main Application (`/main.py`)
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.routes import auth, tasks

app = FastAPI(
    title="Todo API - Hackathon II Phase 2",
    description="Multi-user Todo application with JWT authentication",
    version="2.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # ["http://localhost:3000"] in dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(tasks.router, prefix="/api", tags=["Tasks"])

@app.on_event("startup")
async def startup():
    await init_db()

@app.get("/")
async def root():
    return {"message": "Todo API is running", "version": "2.0.0"}
```

### Configuration (`app/config.py`)
```python
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Authentication
    BETTER_AUTH_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_DAYS: int = 7

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    # Environment
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

---

### SQLModel Database Models

#### User Model (`app/models/user.py`)
```python
from sqlmodel import Field, SQLModel
from datetime import datetime
from typing import Optional
import uuid

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(max_length=255, unique=True, index=True, nullable=False)
    password_hash: str = Field(max_length=255, nullable=False)
    name: str = Field(max_length=100, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    last_login_at: Optional[datetime] = None
```

#### Task Model (`app/models/task.py`)
```python
from sqlmodel import Field, SQLModel, Column
from sqlalchemy import ARRAY, String
from datetime import datetime
from typing import Optional, List
from enum import Enum
import uuid

class Priority(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NONE = "NONE"

class RecurrencePattern(str, Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)
    title: str = Field(max_length=200, nullable=False)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False, nullable=False, index=True)
    priority: Priority = Field(default=Priority.NONE, nullable=False, index=True)
    tags: List[str] = Field(default_factory=list, sa_column=Column(ARRAY(String)))
    due_date: Optional[datetime] = Field(default=None, index=True)
    is_recurring: bool = Field(default=False, nullable=False)
    recurrence_pattern: Optional[RecurrencePattern] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    completed_at: Optional[datetime] = None
```

---

### Pydantic Schemas (Request/Response DTOs)

#### User Schemas (`app/schemas/user.py`)
```python
from pydantic import BaseModel, EmailStr
from datetime import datetime
import uuid

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    name: str
    created_at: datetime

    class Config:
        from_attributes = True  # Enable ORM mode

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    user: UserResponse
    token: str
    expires_at: datetime
```

#### Task Schemas (`app/schemas/task.py`)
```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
import uuid

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: str = "NONE"
    tags: List[str] = []
    due_date: Optional[datetime] = None
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[str] = None
    tags: Optional[List[str]] = None
    due_date: Optional[datetime] = None
    is_recurring: Optional[bool] = None
    recurrence_pattern: Optional[str] = None

class TaskResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: Optional[str]
    completed: bool
    priority: str
    tags: List[str]
    due_date: Optional[datetime]
    is_recurring: bool
    recurrence_pattern: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
```

---

### Authentication & JWT

#### JWT Utilities (`app/utils/jwt.py`)
```python
from jose import jwt, JWTError
from datetime import datetime, timedelta
from app.config import settings
import uuid

def create_jwt_token(user_id: uuid.UUID, email: str, name: str) -> str:
    """Generate JWT token for authenticated user."""
    payload = {
        "user_id": str(user_id),
        "email": email,
        "name": name,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(days=settings.JWT_EXPIRY_DAYS)
    }
    token = jwt.encode(payload, settings.BETTER_AUTH_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token

def verify_jwt_token(token: str) -> dict:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        raise ValueError("Invalid token")
```

#### Password Security (`app/utils/security.py`)
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)
```

#### Auth Middleware (`app/middleware/auth.py`)
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from app.utils.jwt import verify_jwt_token
import uuid

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthCredentials = Depends(security)) -> dict:
    """Extract and verify JWT token from Authorization header."""
    token = credentials.credentials
    try:
        payload = verify_jwt_token(token)
        return payload
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

def verify_user_ownership(user_id_from_url: str, current_user: dict) -> None:
    """Ensure user_id in URL matches user_id in JWT token."""
    if str(current_user["user_id"]) != user_id_from_url:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access another user's resources"
        )
```

---

### API Route Examples

#### Auth Routes (`app/routes/auth.py`)
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import get_session
from app.models.user import User
from app.schemas.user import UserCreate, LoginRequest, LoginResponse, UserResponse
from app.utils.security import hash_password, verify_password
from app.utils.jwt import create_jwt_token
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/signup", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate, session: Session = Depends(get_session)):
    """Create new user account."""
    # Check if email already exists
    statement = select(User).where(User.email == user_data.email)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Create user
    hashed_password = hash_password(user_data.password)
    user = User(
        email=user_data.email,
        password_hash=hashed_password,
        name=user_data.name
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Generate token
    token = create_jwt_token(user.id, user.email, user.name)
    expires_at = datetime.utcnow() + timedelta(days=7)

    return LoginResponse(
        user=UserResponse.from_orm(user),
        token=token,
        expires_at=expires_at
    )

@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest, session: Session = Depends(get_session)):
    """Authenticate user and issue JWT token."""
    statement = select(User).where(User.email == credentials.email)
    user = session.exec(statement).first()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Update last login
    user.last_login_at = datetime.utcnow()
    session.add(user)
    session.commit()

    # Generate token
    token = create_jwt_token(user.id, user.email, user.name)
    expires_at = datetime.utcnow() + timedelta(days=7)

    return LoginResponse(
        user=UserResponse.from_orm(user),
        token=token,
        expires_at=expires_at
    )
```

#### Task Routes (`app/routes/tasks.py`)
```python
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlmodel import Session, select
from typing import List
from app.database import get_session
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.middleware.auth import get_current_user, verify_user_ownership
import uuid

router = APIRouter()

@router.get("/{user_id}/tasks", response_model=List[TaskResponse])
async def list_tasks(
    user_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """List all tasks for authenticated user."""
    verify_user_ownership(user_id, current_user)

    statement = select(Task).where(Task.user_id == uuid.UUID(user_id))
    tasks = session.exec(statement).all()
    return tasks

@router.post("/{user_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: str = Path(...),
    task_data: TaskCreate,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create new task for authenticated user."""
    verify_user_ownership(user_id, current_user)

    task = Task(
        user_id=uuid.UUID(user_id),
        **task_data.model_dump()
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.delete("/{user_id}/tasks/{task_id}", status_code=status.HTTP_200_OK)
async def delete_task(
    user_id: str = Path(...),
    task_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete task (only if owned by authenticated user)."""
    verify_user_ownership(user_id, current_user)

    task = session.get(Task, uuid.UUID(task_id))
    if not task or str(task.user_id) != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    session.delete(task)
    session.commit()
    return {"message": "Task deleted successfully", "deleted_id": task_id}
```

---

### Database Management

#### Database Connection (`app/database.py`)
```python
from sqlmodel import create_engine, Session, SQLModel
from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    echo=False  # Set True for SQL logging in development
)

def init_db():
    """Create all tables."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency for database sessions."""
    with Session(engine) as session:
        yield session
```

---

### Testing Standards

#### Test Configuration (`tests/conftest.py`)
```python
import pytest
from sqlmodel import create_engine, Session, SQLModel
from app.main import app
from app.database import get_session

# Test database (in-memory SQLite)
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})

@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    from fastapi.testclient import TestClient
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
```

#### API Tests (`tests/test_auth.py`)
```python
from fastapi.testclient import TestClient

def test_signup_creates_user(client: TestClient):
    response = client.post("/api/auth/signup", json={
        "email": "test@example.com",
        "password": "SecurePass123!",
        "name": "Test User"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["user"]["email"] == "test@example.com"
    assert "token" in data

def test_login_with_valid_credentials(client: TestClient):
    # First create user
    client.post("/api/auth/signup", json={
        "email": "test@example.com",
        "password": "SecurePass123!",
        "name": "Test User"
    })

    # Then login
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    })
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
```

---

### Type Hints & Linting

#### Mypy Configuration (`pyproject.toml`)
```toml
[tool.mypy]
python_version = "3.13"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

#### Ruff Configuration (`pyproject.toml`)
```toml
[tool.ruff]
line-length = 100
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]
```

---

### Deployment (Hugging Face Spaces)

#### Requirements File
```bash
# pyproject.toml
[tool.uv]
requires-python = ">=3.13"

[project]
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "sqlmodel>=0.0.14",
    "psycopg2-binary>=2.9.9",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "pydantic-settings>=2.0.0",
]
```

---

### Environment Variables

### Required Variables (`.env`)
```bash
DATABASE_URL=postgresql://user:password@ep-xxxx.neon.tech/tododb?sslmode=require
BETTER_AUTH_SECRET=your-256-bit-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRY_DAYS=7
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
ENVIRONMENT=production
```

---

### References

- **Root CLAUDE.md**: `../CLAUDE.md` (SDD workflow)
- **Constitution**: `../.specify/memory/constitution.md` (project principles)
- **API Specs**: `../specs/api/rest-endpoints.md` (complete API documentation)
- **Database Schema**: `../specs/database/schema.md` (PostgreSQL schema)

---


## Phase 3: Backend Development (AI Chatbot Integration)

Phase 3 extends Phase 2 with conversational AI for natural language task management using OpenAI Agents SDK and Model Context Protocol (MCP). This is Phase 3 of 5: Todo AI Chatbot Integration

### Phase 3 Technology Stack
- **AI Framework**: OpenAI Agents SDK
- **MCP Implementation**: Official MCP SDK
- **LLM Provider**: OpenAI API (GPT-4 or later)
- **Backend Architecture**: Stateless FastAPI endpoint + MCP server with database persistence
- **Authentication**: JWT-based, inherits Phase 2 security model
- **Database**: Neon PostgreSQL (shared with Phase 2, adds conversations/messages tables)
- **MCP Tools**: Standardized tools for task operations (add_task, list_tasks, complete_task, delete_task, update_task)

### Phase 3 Architecture
- **Stateless Server**: All conversation state persisted to database; server maintains no state between requests
- **MCP Server**: Exposes task operations as standardized tools for AI agent consumption
- **User Authentication**: JWT-based, verifies user_id matching between token and URL parameters
- **Conversation Persistence**: Conversation and Message models stored in database with user_id filtering
- **Tool Execution**: MCP tools execute with proper user isolation and security validation
- **Multi-User Isolation**: Same security model as Phase 2 - users can only access their own conversations and tasks
- **Error Handling**: Graceful error recovery with descriptive messages for agent interactions

### Phase 3 Database Models
- **Conversation Model**: Stores conversation metadata (user_id, created_at, updated_at)
- **Message Model**: Stores chat history (user_id, conversation_id, role, content, tool_calls, created_at)
- **MCP Tool Integration**: All existing Phase 2 task operations exposed as MCP tools
- **User Isolation**: All queries filtered by user_id for security (parameterized queries only)

### Phase 3 API Endpoints
- **Chat Endpoint**: `POST /api/{user_id}/chat` - Send message & get AI response
- **MCP Tools**: Standardized endpoints for add_task, list_tasks, complete_task, delete_task, update_task
- **Conversation History**: Retrieved from database for context across sessions
- **Authentication**: JWT verification on all endpoints with user_id matching validation
- **Rate Limiting**: Per-user rate limiting for chat endpoints (100 requests per minute)

### MCP Tool Specifications
- **add_task(user_id, title, description)**: Creates new task with validation
- **list_tasks(user_id, status="all"|"pending"|"completed")**: Returns user's tasks
- **complete_task(user_id, task_id)**: Updates task completion status
- **delete_task(user_id, task_id)**: Removes user's task from database
- **update_task(user_id, task_id, title, description)**: Updates task details
- **All tools**: Include proper error handling, user isolation, and validation

### Phase 3 Security Requirements
- **User Isolation**: All MCP tools verify user_id matches authenticated user
- **JWT Validation**: All endpoints verify JWT token and user_id matching
- **Cross-User Access Prevention**: Users cannot access other users' tasks or conversations
- **Tool Validation**: MCP tools validate all parameters and enforce business rules
- **Rate Limiting**: Per-user limits prevent abuse of AI endpoints
- **Input Sanitization**: All user input sanitized before database operations

### Phase 3 Testing Requirements
- **Chat Flow Tests**: 100% coverage for conversation persistence, message validation, tool execution
- **MCP Tool Tests**: 100% coverage for all 5 core tools (add_task, list_tasks, complete_task, delete_task, update_task)
- **Security Tests**: 100% coverage for user isolation, cross-user access prevention, JWT validation
- **Agent Behavior Tests**: 80%+ coverage for natural language understanding and intent recognition
- **Error Recovery Tests**: 100% coverage for tool failures, timeout handling, partial success scenarios
- **Database Tests**: 100% coverage for conversation/message persistence and user filtering

### Phase 3 Integration Points
- **Shared Database**: Uses same Neon PostgreSQL database as Phase 2 (users, tasks tables)
- **Shared Authentication**: Inherits JWT-based authentication from Phase 2
- **MCP Server**: Exposes Phase 2 database operations as standardized tools for AI consumption
- **Security Model**: Maintains same user isolation and access control as Phase 2
- **API Contracts**: MCP tools follow same validation and error handling patterns as Phase 2


## Phase 4: Backend Containerization and Kubernetes Deployment

Phase 4 extends Phase 3 with containerization and Kubernetes deployment. This is Phase 4 of 5: Local Kubernetes Deployment

### Phase 4 Containerization Requirements
- **Dockerfile**: Create optimized Dockerfile for FastAPI backend with multi-stage build
- **Base Image**: Use python:3.13-slim or newer stable version for smaller footprint
- **UV Package Manager**: Use UV for faster Python dependency installation in container
- **Layer Caching**: Optimize Docker layers for faster builds (dependencies in separate layer)
- **Security**: Run container as non-root user, minimal packages installed
- **Environment Variables**: Support configurable environment variables for different deployments
- **Health Checks**: Implement HTTP-based liveness/readiness probes for FastAPI app
- **Resource Limits**: Define CPU and memory constraints for predictable performance

### Phase 4 Kubernetes Integration
- **Deployment**: Deploy FastAPI application as Kubernetes Deployment with rolling updates
- **Service**: Expose backend via ClusterIP Service for internal communication
- **Database Connection**: Maintain connection to Neon PostgreSQL (external service reference)
- **ConfigMap**: Store non-sensitive configuration in ConfigMap
- **Secrets**: Store sensitive data (DB URLs, API keys, JWT secrets) in Kubernetes Secrets
- **Horizontal Pod Autoscaler**: Configure HPA based on CPU/memory metrics
- **Resource Requests/Limits**: Define resource requirements for predictable performance
- **Service Discovery**: Use Kubernetes DNS for internal service communication

### Phase 4 MCP Server in Kubernetes
- **MCP Server Deployment**: Deploy MCP server as part of Kubernetes cluster
- **Stateless Architecture**: Ensure MCP server remains stateless with all state persisted to database
- **API Gateway**: Route MCP endpoints through same ingress as main API
- **Load Balancing**: Distribute MCP requests across multiple pods
- **Health Monitoring**: Monitor MCP server health and performance metrics

### Phase 4 DevOps Integration
- **Helm Chart**: Package backend application using Helm for configuration management
- **CI/CD Pipeline**: Integrate with AI-assisted CI/CD pipeline for automated deployments
- **Monitoring**: Implement structured logging with correlation IDs for observability
- **Health Monitoring**: Implement health endpoints for readiness/liveness probes
- **Environment Consistency**: Ensure consistent behavior across development, staging, and production
- **AI-Assisted Operations**: Use Gordon for Docker builds, kubectl-ai and kagent for Kubernetes operations

### Phase 4 Testing Requirements
- **Container Tests**: Validate Docker image build process and security
- **Deployment Tests**: Verify successful deployment to Kubernetes cluster
- **Integration Tests**: Test backend services in Kubernetes environment
- **Performance Tests**: Validate performance characteristics in containerized environment
- **Security Tests**: Verify security best practices in containerized deployment
- **MCP Tool Tests**: Validate MCP tools function correctly in Kubernetes environment
- **Database Connectivity Tests**: Verify database connections work properly from Kubernetes pods

---


**Version**: 1.0.0
**Last Updated**: 2026-01-02
**Next Review**: After `/sp.plan` completion

---