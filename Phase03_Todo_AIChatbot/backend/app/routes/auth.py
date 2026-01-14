from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import get_session
from app.models.user import User, UserCreate, UserRead, UserLogin
from app.utils.security import get_password_hash, verify_password
from app.utils.jwt import create_access_token
from datetime import timedelta, datetime
from typing import Dict, Any
import uuid

router = APIRouter()

@router.post("/signup", status_code=status.HTTP_201_CREATED, summary="Register a new user", description="Create a new user account and generate a JWT access token valid for 7 days.")
async def signup(user: UserCreate, session: Session = Depends(get_session)) -> Dict[str, Any]:
    """
    Create a new user account with automatic email verification.

    **Parameters:**
    - **user**: UserCreate object containing:
      - email (required): User's email address (must be unique)
      - password (required): User's password (will be hashed using bcrypt)
      - name (required): User's display name

    **Returns:**
    - user: UserRead object with user details
    - token: JWT access token valid for 7 days
    - token_type: Always "bearer"

    **Example:**
    ```
    POST /api/auth/signup
    {
      "email": "user@example.com",
      "password": "SecurePass123!",
      "name": "John Doe"
    }
    ```

    **Response:**
    ```json
    {
      "user": {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "email": "user@example.com",
        "name": "John Doe",
        "email_verified": true,
        "created_at": "2026-01-08T10:30:00"
      },
      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "bearer"
    }
    ```

    **Status Codes:**
    - 201: User created successfully
    - 409: Email already registered
    - 422: Validation error in request body
    """
    # Check if user already exists
    existing_user = session.exec(select(User).where(User.email == user.email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Create new user with email_verified = True (Option B: Instant Switch)
    # All new users are immediately verified since we marked existing users as verified
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        password_hash=hashed_password,
        name=user.name,
        email_verified=True  # Auto-verify (email verification feature prepared but not enforced yet)
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    # Create access token
    access_token_expires = timedelta(days=7)
    access_token = create_access_token(
        data={"sub": str(db_user.id), "email": db_user.email, "name": db_user.name},
        expires_delta=access_token_expires
    )

    return {
        "user": UserRead.model_validate(db_user),
        "token": access_token,
        "token_type": "bearer"
    }


@router.post("/login", summary="Login user", description="Authenticate a user with email and password, returning a JWT access token valid for 7 days.")
async def login(user_credentials: UserLogin, session: Session = Depends(get_session)) -> Dict[str, Any]:
    """
    Authenticate user and return JWT token.

    **Parameters:**
    - **user_credentials**: UserLogin object containing:
      - email (required): User's email address
      - password (required): User's password

    **Returns:**
    - user: UserRead object with user details
    - token: JWT access token valid for 7 days
    - token_type: Always "bearer"

    **Example:**
    ```
    POST /api/auth/login
    {
      "email": "user@example.com",
      "password": "SecurePass123!"
    }
    ```

    **Response:**
    ```json
    {
      "user": {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "email": "user@example.com",
        "name": "John Doe",
        "email_verified": true,
        "created_at": "2026-01-08T10:30:00",
        "last_login_at": "2026-01-08T15:45:00"
      },
      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "bearer"
    }
    ```

    **Status Codes:**
    - 200: Login successful
    - 401: Invalid email or password
    - 422: Validation error in request body

    **Note:**
    The JWT token should be included in the Authorization header for authenticated requests:
    ```
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    ```
    """
    # Find user by email
    user = session.exec(select(User).where(User.email == user_credentials.email)).first()

    if not user or not verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login
    user.last_login_at = datetime.utcnow()
    session.add(user)
    session.commit()

    # Create access token
    access_token_expires = timedelta(days=7)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "name": user.name},
        expires_delta=access_token_expires
    )

    return {
        "user": UserRead.model_validate(user),
        "token": access_token,
        "token_type": "bearer"
    }


@router.post("/logout", summary="Logout user", description="Logout endpoint for client-side token cleanup. Since JWT is stateless, the token remains valid until expiry.")
async def logout():
    """
    Logout user (stateless JWT implementation).

    **Note:**
    This endpoint returns a success message for client-side cleanup. Since JWT tokens are stateless and self-contained,
    the token remains valid until it expires (7 days after creation). Clients should:
    1. Delete the token from local storage/memory
    2. Clear any user session data
    3. Redirect to the login page

    **Returns:**
    - message: Success message

    **Example:**
    ```
    POST /api/auth/logout
    ```

    **Response:**
    ```json
    {
      "message": "Successfully logged out"
    }
    ```

    **Status Codes:**
    - 200: Logout successful
    """
    return {"message": "Successfully logged out"}