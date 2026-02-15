from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import get_session
from app.models.user import User, UserRead, UserUpdate
from app.utils.security import get_password_hash, verify_password
from app.middleware.auth import get_current_user
from pydantic import BaseModel, Field
from typing import Dict
import uuid
from datetime import datetime

router = APIRouter()

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=6)

@router.put("/profile", response_model=UserRead)
async def update_profile(
    user_update: UserUpdate,
    current_user: Dict = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> UserRead:
    """Update current user's profile information."""
    # current_user is a dict from JWT payload, get the user_id
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    db_user = session.get(User, uuid.UUID(user_id))
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update fields if provided
    if user_update.name is not None:
        db_user.name = user_update.name

    if user_update.email is not None and user_update.email != db_user.email:
        # Check if email is already taken
        existing_user = session.exec(select(User).where(User.email == user_update.email)).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        db_user.email = user_update.email

    db_user.updated_at = datetime.utcnow()
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return UserRead.model_validate(db_user)

@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: Dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Change current user's password."""
    # current_user is a dict from JWT payload, get the user_id
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    db_user = session.get(User, uuid.UUID(user_id))
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify current password
    if not verify_password(password_data.current_password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect current password"
        )

    # Update password
    db_user.password_hash = get_password_hash(password_data.new_password)
    db_user.updated_at = datetime.utcnow()
    session.add(db_user)
    session.commit()

    return {"message": "Password updated successfully"}

@router.delete("/account")
async def delete_account(
    current_user: Dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete the current user's account and all associated data."""
    from app.models.task import Task

    # current_user is a dict from JWT payload, get the user_id
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    db_user = session.get(User, uuid.UUID(user_id))
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # First, delete all tasks associated with this user
    user_tasks = session.exec(select(Task).where(Task.user_id == uuid.UUID(user_id))).all()
    for task in user_tasks:
        session.delete(task)

    # Then delete the user
    session.delete(db_user)
    session.commit()

    return {"message": "Account deleted successfully"}
