from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Optional
from app.utils.jwt import verify_token
from app.models.user import UserRead

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """Get the current user from the JWT token in the Authorization header."""
    token = credentials.credentials
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if token has expired
    import datetime
    if "exp" in payload and datetime.datetime.utcnow() > datetime.datetime.fromtimestamp(payload["exp"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Standardize the payload to include user_id
    if "sub" in payload and "user_id" not in payload:
        payload["user_id"] = payload["sub"]

    return payload

def verify_user_access(user_id_from_token: str, user_id_from_path: str) -> bool:
    """Verify that the user_id in the token matches the user_id in the path."""
    return user_id_from_token == user_id_from_path