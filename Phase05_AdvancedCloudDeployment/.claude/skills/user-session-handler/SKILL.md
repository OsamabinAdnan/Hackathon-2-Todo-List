---
name: user-session-handler
description: Generate code for session creation on login, invalidation on logout, and filtering data to user-owned tasks. Use when (1) Implementing login endpoints that create sessions and issue JWT tokens, (2) Building logout endpoints that invalidate tokens (blacklist or database flag), (3) Filtering database queries to show only user-owned data (Task.user_id == current_user.id), (4) Implementing token refresh for extending sessions without re-authentication, (5) Handling edge cases like concurrent sessions, device management, or "logout all devices", (6) Preparing for multi-language support with user preferences in session data.
---

# User Session Handler Skill

Generate code for managing user sessions with JWT-based authentication, including session creation on login, invalidation on logout, and strict data filtering to ensure users only access their own data.

## Core Capabilities

### 1. Session Creation on Login

Generate JWT tokens and establish user sessions upon successful authentication:

```python
# app/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import get_session
from app.models import User
from app.schemas import LoginRequest, LoginResponse, UserResponse
from app.auth.jwt import create_access_token, create_refresh_token
from app.auth.password import verify_password

router = APIRouter(tags=["authentication"])

@router.post("/api/auth/login", response_model=LoginResponse)
async def login(
    credentials: LoginRequest,
    session: Session = Depends(get_session)
):
    """
    Authenticate user and create session with JWT tokens.

    Returns:
        - access_token: Short-lived token for API requests (7 days)
        - refresh_token: Long-lived token for obtaining new access tokens (30 days)
        - user: User profile data
    """
    # Find user by email
    statement = select(User).where(User.email == credentials.email)
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Create session tokens
    access_token = create_access_token(user_id=user.id)
    refresh_token = create_refresh_token(user_id=user.id)

    # Optional: Store session metadata in database
    # (useful for device management, "logout all devices")
    # await create_user_session(session, user.id, device_info)

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )
```

**Request/Response Models:**
```python
# app/schemas.py
from pydantic import BaseModel, EmailStr, Field

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}
```

### 2. Session Invalidation on Logout

Implement logout with token blacklisting or database session invalidation:

**Option A: Token Blacklist (Redis recommended)**
```python
# app/auth/blacklist.py
from redis import Redis
from datetime import timedelta
import os

redis_client = Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

def blacklist_token(token: str, expires_in_seconds: int):
    """
    Add token to blacklist with expiration matching token TTL.
    """
    redis_client.setex(
        name=f"blacklist:{token}",
        time=expires_in_seconds,
        value="1"
    )

def is_token_blacklisted(token: str) -> bool:
    """
    Check if token is blacklisted.
    """
    return redis_client.exists(f"blacklist:{token}") == 1

# app/routes/auth.py
from app.auth.jwt import decode_access_token
from app.auth.blacklist import blacklist_token

@router.post("/api/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Logout user by blacklisting access token.
    Client should delete refresh token from storage.
    """
    token = credentials.credentials

    # Decode to get expiration time
    payload = decode_access_token(token)
    exp_timestamp = payload.get("exp")

    # Calculate remaining TTL
    from datetime import datetime
    remaining_seconds = exp_timestamp - int(datetime.utcnow().timestamp())

    if remaining_seconds > 0:
        blacklist_token(token, remaining_seconds)

    return None  # 204 No Content
```

**Option B: Database Session Tracking (for "logout all devices")**
```python
# app/models.py
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
import uuid

class UserSession(SQLModel, table=True):
    __tablename__ = "user_sessions"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    refresh_token_hash: str = Field(max_length=255)  # Hash of refresh token
    device_info: Optional[str] = Field(None, max_length=500)
    ip_address: Optional[str] = Field(None, max_length=45)
    created_at: datetime = Field(default_factory=datetime.now)
    last_active: datetime = Field(default_factory=datetime.now)
    is_active: bool = Field(default=True, index=True)

    # Relationship
    user: User = Relationship(back_populates="sessions")

# app/routes/auth.py
@router.post("/api/auth/logout-all", status_code=status.HTTP_204_NO_CONTENT)
async def logout_all_devices(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Invalidate all sessions for the current user across all devices.
    """
    # Mark all user sessions as inactive
    statement = (
        select(UserSession)
        .where(UserSession.user_id == current_user.id)
        .where(UserSession.is_active == True)
    )
    sessions_to_invalidate = session.exec(statement).all()

    for user_session in sessions_to_invalidate:
        user_session.is_active = False
        user_session.last_active = datetime.now()

    session.commit()

    return None
```

### 3. Data Filtering for User Isolation

Ensure all database queries filter by authenticated user to prevent data leaks:

```python
# app/routes/tasks.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.models import Task, User
from app.database import get_session
from app.auth.dependencies import get_current_user
from typing import Optional

router = APIRouter(tags=["tasks"])

@router.get("/api/{user_id}/tasks")
async def list_tasks(
    user_id: str,
    completed: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    List tasks with strict user isolation filtering.

    Security:
        1. Verify user_id matches authenticated user
        2. Filter all queries by Task.user_id == current_user.id
    """
    # User isolation check
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Cannot access another user's data"
        )

    # Build query with user filter
    query = select(Task).where(Task.user_id == current_user.id)

    # Apply optional filters
    if completed is not None:
        query = query.where(Task.completed == completed)

    # Execute query
    tasks = session.exec(query).all()

    return {"tasks": tasks}

@router.get("/api/{user_id}/tasks/{task_id}")
async def get_task(
    user_id: str,
    task_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get single task with ownership verification.
    """
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    # Fetch task
    task = session.get(Task, task_id)

    # Verify ownership
    if not task or task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task

@router.delete("/api/{user_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: str,
    task_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete task with ownership verification.
    """
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    task = session.get(Task, task_id)

    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    session.delete(task)
    session.commit()

    return None
```

### 4. Token Refresh for Session Extension

Allow users to extend sessions without re-authentication:

```python
# app/routes/auth.py
@router.post("/api/auth/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_request: RefreshTokenRequest,
    session: Session = Depends(get_session)
):
    """
    Exchange refresh token for new access token.

    Edge Cases Handled:
        - Expired refresh token
        - Invalid token type (must be 'refresh')
        - User not found (deleted account)
        - Token blacklisted (after logout)
    """
    try:
        # Decode refresh token
        payload = decode_access_token(refresh_request.refresh_token)

        # Verify token type
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type: expected refresh token"
            )

        # Check if token is blacklisted (if using blacklist)
        if is_token_blacklisted(refresh_request.refresh_token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked"
            )

        user_id = payload.get("user_id")
        user = session.get(User, user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        # Generate new access token (refresh token remains valid)
        new_access_token = create_access_token(user_id=user.id)

        # Optional: Update last_active timestamp in database session
        # await update_session_activity(user_id, refresh_request.refresh_token)

        return TokenResponse(
            access_token=new_access_token,
            token_type="bearer"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

### 5. Concurrent Session Management

Track and manage multiple active sessions per user:

```python
# app/services/session_service.py
from sqlmodel import Session, select
from app.models import UserSession
from datetime import datetime
from hashlib import sha256

class SessionService:
    def __init__(self, db_session: Session):
        self.db = db_session

    def create_session(
        self,
        user_id: str,
        refresh_token: str,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> UserSession:
        """
        Create new user session record.
        """
        # Hash refresh token for storage (never store plain tokens)
        token_hash = sha256(refresh_token.encode()).hexdigest()

        session = UserSession(
            user_id=user_id,
            refresh_token_hash=token_hash,
            device_info=device_info,
            ip_address=ip_address
        )

        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        return session

    def get_active_sessions(self, user_id: str) -> list[UserSession]:
        """
        Get all active sessions for a user.
        """
        statement = (
            select(UserSession)
            .where(UserSession.user_id == user_id)
            .where(UserSession.is_active == True)
            .order_by(UserSession.last_active.desc())
        )

        return self.db.exec(statement).all()

    def invalidate_session(self, session_id: str):
        """
        Invalidate specific session.
        """
        session = self.db.get(UserSession, session_id)
        if session:
            session.is_active = False
            session.last_active = datetime.now()
            self.db.commit()

    def cleanup_expired_sessions(self, days: int = 30):
        """
        Remove sessions older than specified days.
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        statement = (
            select(UserSession)
            .where(UserSession.last_active < cutoff_date)
        )

        expired_sessions = self.db.exec(statement).all()

        for session in expired_sessions:
            self.db.delete(session)

        self.db.commit()

# app/routes/auth.py
@router.get("/api/auth/sessions", response_model=list[SessionResponse])
async def list_sessions(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    List all active sessions for current user.
    """
    service = SessionService(session)
    active_sessions = service.get_active_sessions(current_user.id)

    return [SessionResponse.model_validate(s) for s in active_sessions]

@router.delete("/api/auth/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Revoke specific session (e.g., "logout from other device").
    """
    # Verify session belongs to current user
    user_session = session.get(UserSession, session_id)

    if not user_session or user_session.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    service = SessionService(session)
    service.invalidate_session(session_id)

    return None
```

### 6. Multi-Language Support Preparation

Store user preferences in session for internationalization:

```python
# app/models.py
class User(SQLModel, table=True):
    # ... existing fields ...
    preferred_language: str = Field(default="en", max_length=5)  # ISO 639-1 code
    timezone: str = Field(default="UTC", max_length=50)

# app/routes/auth.py
@router.post("/api/auth/login", response_model=LoginResponse)
async def login(credentials: LoginRequest, ...):
    # ... authentication logic ...

    # Include user preferences in response
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
        preferences={
            "language": user.preferred_language,
            "timezone": user.timezone
        }
    )

# app/routes/users.py
@router.patch("/api/{user_id}/preferences")
async def update_preferences(
    user_id: str,
    preferences: UserPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update user preferences (language, timezone).
    """
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    if preferences.language:
        current_user.preferred_language = preferences.language
    if preferences.timezone:
        current_user.timezone = preferences.timezone

    session.commit()
    session.refresh(current_user)

    return UserResponse.model_validate(current_user)

class UserPreferencesUpdate(BaseModel):
    language: Optional[str] = Field(None, pattern="^[a-z]{2}(-[A-Z]{2})?$")
    timezone: Optional[str] = None
```

## Edge Cases and Best Practices

### 1. Handle Token Expiration Gracefully
```python
# Frontend should catch 401 errors and attempt refresh
# app/middleware/auth_middleware.py
@app.exception_handler(HTTPException)
async def auth_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 401:
        return JSONResponse(
            status_code=401,
            content={
                "detail": exc.detail,
                "action": "refresh_token"  # Hint to frontend
            }
        )
    raise exc
```

### 2. Prevent Session Fixation
```python
# Always generate new tokens on password change
@router.post("/api/auth/change-password")
async def change_password(
    password_change: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verify old password, update to new password
    # ...

    # Invalidate all existing sessions
    service = SessionService(session)
    for user_session in service.get_active_sessions(current_user.id):
        service.invalidate_session(user_session.id)

    # Generate new tokens
    new_access_token = create_access_token(user_id=current_user.id)
    new_refresh_token = create_refresh_token(user_id=current_user.id)

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )
```

### 3. Rate Limiting for Login/Refresh
```python
# Use slowapi or custom rate limiting
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/api/auth/login")
@limiter.limit("5/minute")  # 5 attempts per minute
async def login(...):
    ...
```

## Quality Checklist

- [ ] Login endpoint generates both access and refresh tokens
- [ ] Logout endpoint blacklists tokens or marks session as inactive
- [ ] All data queries filter by current_user.id
- [ ] User ID from token is verified against URL path parameters
- [ ] Token refresh endpoint validates token type and user existence
- [ ] Concurrent sessions are tracked in database (optional)
- [ ] "Logout all devices" functionality implemented
- [ ] User preferences (language, timezone) stored and returned
- [ ] Session cleanup job scheduled for expired sessions
- [ ] Rate limiting applied to authentication endpoints

## References

- **Auth Spec**: `@specs/features/authentication.md` for complete session requirements
- **API Endpoints**: `@specs/api/rest-endpoints.md` for session-related routes
- **JWT Token Management**: `.claude/skills/jwt-token-management/SKILL.md` for token handling
