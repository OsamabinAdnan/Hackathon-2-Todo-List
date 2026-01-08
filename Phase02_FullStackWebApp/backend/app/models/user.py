from sqlmodel import Field, SQLModel
from datetime import datetime
from typing import Optional
import uuid
from pydantic import BaseModel, field_validator

class UserBase(SQLModel):
    email: str = Field(unique=True, index=True, max_length=255)
    name: str = Field(max_length=100)

class User(UserBase, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)
    email_verified: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    last_login_at: Optional[datetime] = None

class UserCreate(UserBase):
    password: str

class UserRead(BaseModel):
    id: uuid.UUID
    email: str
    name: str
    email_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: str
    password: str

class UserUpdate(SQLModel):
    name: Optional[str] = Field(default=None, max_length=100)
    email: Optional[str] = Field(default=None, max_length=255)