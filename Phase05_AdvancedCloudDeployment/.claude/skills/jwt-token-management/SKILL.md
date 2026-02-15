---
name: jwt-token-management
description: Configure Better Auth to issue/verify JWT tokens with header extraction, decoding in FastAPI middleware, expiry management, and secure secret handling. Use when (1) Setting up JWT token generation on signup/login with HS256 algorithm, (2) Implementing Bearer token extraction from Authorization headers in FastAPI, (3) Configuring token expiry (default 7 days) and refresh logic, (4) Storing JWT secrets securely in environment variables, (5) Validating token claims (user_id, exp, iat) in authentication middleware, (6) Ensuring user ID from token matches URL path parameters for user isolation.
---

# JWT Token Management Skill

Configure Better Auth with FastAPI to issue, verify, and manage JWT tokens for stateless authentication with proper security practices.

## Core Capabilities

### 1. Token Generation

Generate JWT tokens on user signup/login with appropriate claims and expiry:

```python
# app/auth/jwt.py
from datetime import datetime, timedelta
import jwt
import os
from typing import Optional

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable must be set")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7  # Default 7-day expiry

def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Generate JWT access token with user_id claim.

    Args:
        user_id: Unique user identifier to embed in token
        expires_delta: Optional custom expiration time (defaults to 7 days)

    Returns:
        Encoded JWT token string
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)

    to_encode = {
        "user_id": user_id,
        "exp": expire,
        "iat": datetime.utcnow(),  # Issued at
        "type": "access"
    }

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

**Usage in Login Endpoint:**
```python
# app/routes/auth.py
from app.auth.jwt import create_access_token

@router.post("/api/auth/login", response_model=LoginResponse)
async def login(
    credentials: LoginRequest,
    session: Session = Depends(get_session)
):
    # Verify credentials (check password hash)
    user = authenticate_user(session, credentials.email, credentials.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Generate JWT token
    access_token = create_access_token(user_id=user.id)

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )
```

### 2. Token Verification and Decoding

Extract and validate JWT tokens from Authorization headers:

```python
# app/auth/jwt.py
from fastapi import HTTPException, status
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

def decode_access_token(token: str) -> dict:
    """
    Decode and validate JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload with user_id and claims

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id: str = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user_id claim"
            )

        return payload

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )

    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )
```

### 3. FastAPI Authentication Middleware

Implement dependency injection for protected routes:

```python
# app/auth/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session
from app.auth.jwt import decode_access_token
from app.database import get_session
from app.models import User

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    """
    Extract JWT token from Authorization header and return authenticated user.

    Usage:
        @router.get("/api/{user_id}/tasks")
        async def get_tasks(current_user: User = Depends(get_current_user)):
            ...

    Returns:
        Authenticated User object from database

    Raises:
        HTTPException: 401 if token invalid or user not found
    """
    token = credentials.credentials

    # Decode and validate token
    payload = decode_access_token(token)
    user_id = payload.get("user_id")

    # Fetch user from database
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user
```

### 4. User Isolation Enforcement

Ensure user_id in token matches URL path parameters:

```python
# app/routes/tasks.py
from fastapi import APIRouter, Depends, HTTPException, status
from app.auth.dependencies import get_current_user
from app.models import User

router = APIRouter()

@router.get("/api/{user_id}/tasks")
async def list_tasks(
    user_id: str,  # From URL path
    current_user: User = Depends(get_current_user)  # From JWT token
):
    """
    List tasks for a user with strict user isolation.

    Security: Verify user_id from URL matches authenticated user.
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Cannot access another user's data"
        )

    # Proceed with query - user is authorized
    tasks = session.exec(
        select(Task).where(Task.user_id == user_id)
    ).all()

    return {"tasks": tasks}
```

### 5. Environment Variable Configuration

Securely manage JWT secrets and expiry settings:

```bash
# .env
JWT_SECRET_KEY=your-super-secret-key-change-in-production-min-32-chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_DAYS=7
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30  # For token refresh feature
```

**Loading Configuration:**
```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_DAYS: int = 7
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### 6. Token Refresh Implementation

Implement token refresh for long-lived sessions:

```python
# app/auth/jwt.py
def create_refresh_token(user_id: str) -> str:
    """
    Generate long-lived refresh token (30 days default).
    Used to obtain new access tokens without re-authentication.
    """
    expire = datetime.utcnow() + timedelta(days=30)

    to_encode = {
        "user_id": user_id,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    }

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# app/routes/auth.py
@router.post("/api/auth/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    session: Session = Depends(get_session)
):
    """
    Issue new access token using valid refresh token.
    """
    payload = decode_access_token(refresh_token)

    # Verify token type
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )

    user_id = payload.get("user_id")
    user = session.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    # Generate new access token
    new_access_token = create_access_token(user_id=user.id)

    return TokenResponse(
        access_token=new_access_token,
        token_type="bearer"
    )
```

## Security Best Practices

### 1. Secret Key Requirements
- **Minimum Length**: 32 characters (256 bits)
- **Randomness**: Use cryptographically secure random generator
- **Storage**: Environment variables only, NEVER commit to version control
- **Rotation**: Plan for key rotation (invalidates existing tokens)

**Generate Strong Secret:**
```python
import secrets
secret_key = secrets.token_urlsafe(32)
print(f"JWT_SECRET_KEY={secret_key}")
```

### 2. Token Claims Validation
Always validate these claims:
- `exp` (expiration time) - checked automatically by PyJWT
- `iat` (issued at) - for detecting token reuse
- `user_id` - must exist in database
- `type` - distinguish access vs refresh tokens

### 3. HTTPS Requirement
JWT tokens MUST be transmitted over HTTPS in production:
```python
# app/main.py
if settings.ENVIRONMENT == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
```

### 4. Token Storage (Frontend)
**Recommended**: httpOnly cookies (not accessible via JavaScript)
**Alternative**: localStorage with XSS protection

```python
# Set token in httpOnly cookie
from fastapi.responses import Response

@router.post("/api/auth/login")
async def login(response: Response, ...):
    access_token = create_access_token(user_id=user.id)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # Prevent XSS
        secure=True,    # HTTPS only
        samesite="lax", # CSRF protection
        max_age=7 * 24 * 60 * 60  # 7 days in seconds
    )

    return {"message": "Login successful"}
```

## Error Handling Patterns

```python
# app/auth/exceptions.py
class TokenExpiredError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please login again.",
            headers={"WWW-Authenticate": "Bearer"}
        )

class InvalidTokenError(HTTPException):
    def __init__(self, detail: str = "Invalid authentication token"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )

class InsufficientPermissionsError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access this resource"
        )
```

## Testing Strategy

```python
# tests/test_jwt.py
import pytest
from datetime import timedelta
from app.auth.jwt import create_access_token, decode_access_token

def test_create_access_token():
    """Test JWT token generation with valid user_id"""
    user_id = "test-user-123"
    token = create_access_token(user_id)

    assert token is not None
    assert isinstance(token, str)

    # Decode and verify claims
    payload = decode_access_token(token)
    assert payload["user_id"] == user_id
    assert "exp" in payload
    assert "iat" in payload

def test_expired_token():
    """Test that expired tokens raise proper exception"""
    user_id = "test-user-123"

    # Create token that expires immediately
    token = create_access_token(
        user_id=user_id,
        expires_delta=timedelta(seconds=-1)
    )

    with pytest.raises(HTTPException) as exc_info:
        decode_access_token(token)

    assert exc_info.value.status_code == 401
    assert "expired" in exc_info.value.detail.lower()

def test_user_isolation(client, auth_headers):
    """Test that users cannot access other users' data"""
    # User A tries to access User B's tasks
    response = client.get(
        "/api/user-b-id/tasks",
        headers=auth_headers["user_a"]  # User A's token
    )

    assert response.status_code == 403
    assert "forbidden" in response.json()["detail"].lower()
```

## Quality Checklist

- [ ] JWT_SECRET_KEY is at least 32 characters and stored in .env
- [ ] Token expiry is configured (default 7 days for access tokens)
- [ ] decode_access_token validates exp, iat, and user_id claims
- [ ] HTTPBearer security scheme extracts tokens from Authorization header
- [ ] get_current_user dependency fetches user from database
- [ ] All protected routes verify user_id from token matches URL parameter
- [ ] Token refresh endpoint implemented with separate refresh token type
- [ ] HTTPS enforcement configured for production
- [ ] Error handling returns 401 for invalid/expired tokens, 403 for permission issues
- [ ] Tests cover token generation, validation, expiry, and user isolation

## References

- **Auth Spec**: `@specs/features/authentication.md` for complete authentication requirements
- **API Endpoints**: `@specs/api/rest-endpoints.md` for protected route definitions
- **PyJWT Documentation**: https://pyjwt.readthedocs.io for token encoding/decoding
- **FastAPI Security**: https://fastapi.tiangolo.com/tutorial/security/ for OAuth2 patterns
