---
name: api-endpoint-builder
description: Create RESTful FastAPI endpoints with Pydantic models for request/response validation, SQLModel database integration, JWT authentication, and pagination. Use when (1) Implementing API endpoints from @specs/api/rest-endpoints.md (e.g., GET/POST/PUT/DELETE /api/{user_id}/tasks), (2) Adding request validation with Pydantic BaseModel schemas, (3) Implementing pagination for list endpoints with page/limit parameters, (4) Creating response serialization with proper HTTP status codes, (5) Adding sorting/filtering query parameters, (6) Ensuring user isolation with JWT token validation middleware.
---

# API Endpoint Builder

Create production-ready FastAPI endpoints with comprehensive request validation, response serialization, authentication, and database integration following RESTful principles.

## Endpoint Building Workflow

### 1. Analyze API Specification

Read `@specs/api/rest-endpoints.md` to extract:
- HTTP method (GET, POST, PUT, DELETE, PATCH)
- URL pattern (e.g., `/api/{user_id}/tasks`, `/api/{user_id}/tasks/{id}`)
- Path parameters (user_id, task_id)
- Query parameters (page, limit, priority, status, sort_by)
- Request body schema
- Response schema
- HTTP status codes (200, 201, 400, 401, 404, 422)
- Authentication requirements

### 2. Create Pydantic Request Models

Define validation schemas for request bodies:

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

class TaskCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000)
    priority: str = Field("NONE", pattern="^(HIGH|MEDIUM|LOW|NONE)$")
    tags: Optional[list[str]] = Field(None, max_length=10)
    due_date: Optional[datetime] = None
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = Field(None, pattern="^(DAILY|WEEKLY|MONTHLY)$")

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        if v:
            for tag in v:
                if len(tag) > 20:
                    raise ValueError("Each tag must be 20 characters or less")
        return v

    @field_validator('due_date')
    @classmethod
    def validate_due_date(cls, v):
        if v and v < datetime.now():
            raise ValueError("Due date must be in the future")
        return v

class TaskUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[str] = Field(None, pattern="^(HIGH|MEDIUM|LOW|NONE)$")
    tags: Optional[list[str]] = None
    due_date: Optional[datetime] = None
    completed: Optional[bool] = None
```

### 3. Create Response Models

Define serialization schemas:

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TaskResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    priority: str
    tags: list[str]
    due_date: Optional[datetime]
    is_recurring: bool
    recurrence_pattern: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

    model_config = {"from_attributes": True}

class TaskListResponse(BaseModel):
    tasks: list[TaskResponse]
    pagination: dict

class PaginationInfo(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int
```

### 4. Implement CRUD Endpoints

**GET List with Pagination/Filtering:**
```python
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlmodel import Session, select, func
from typing import Optional

router = APIRouter(prefix="/api/{user_id}", tags=["tasks"])

@router.get("/tasks", response_model=TaskListResponse)
async def list_tasks(
    user_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    priority: Optional[str] = Query(None, pattern="^(HIGH|MEDIUM|LOW|NONE)$"),
    status: Optional[str] = Query(None, pattern="^(todo|done|all)$"),
    sort_by: Optional[str] = Query("created_at", pattern="^(priority|created_at|due_date|title)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Verify user_id matches authenticated user
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access")

    # Build query
    query = select(Task).where(Task.user_id == user_id)

    # Apply filters
    if priority:
        query = query.where(Task.priority == priority)
    if status == "todo":
        query = query.where(Task.completed == False)
    elif status == "done":
        query = query.where(Task.completed == True)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = session.exec(count_query).one()

    # Apply sorting
    sort_field = getattr(Task, sort_by)
    if order == "desc":
        query = query.order_by(sort_field.desc())
    else:
        query = query.order_by(sort_field.asc())

    # Apply pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)

    tasks = session.exec(query).all()

    return TaskListResponse(
        tasks=[TaskResponse.model_validate(task) for task in tasks],
        pagination={
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit
        }
    )
```

**POST Create:**
```python
@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: str,
    task_data: TaskCreateRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access")

    task = Task(**task_data.model_dump(), user_id=user_id)
    session.add(task)
    session.commit()
    session.refresh(task)

    return TaskResponse.model_validate(task)
```

**GET Single:**
```python
@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    user_id: str,
    task_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return TaskResponse.model_validate(task)
```

**PUT Update:**
```python
@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    user_id: str,
    task_id: str,
    task_data: TaskUpdateRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    # Update only provided fields
    for field, value in task_data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)

    task.updated_at = datetime.now()
    session.commit()
    session.refresh(task)

    return TaskResponse.model_validate(task)
```

**DELETE:**
```python
@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: str,
    task_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    session.delete(task)
    session.commit()
```

### 5. Authentication Dependency

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return user
```

## Endpoint Patterns

See `references/endpoint-patterns.md` for complete examples of:
- Search endpoints with full-text search
- Batch operations (bulk create/update/delete)
- Partial updates with PATCH
- Custom actions (e.g., `/tasks/{id}/complete`, `/tasks/{id}/archive`)
- File upload endpoints with multipart/form-data

## Quality Checklist

- [ ] Endpoint follows RESTful URL conventions from spec
- [ ] Request validation with Pydantic models
- [ ] Response serialization with proper models
- [ ] Authentication/authorization enforced
- [ ] User isolation verified (user_id from token matches URL param)
- [ ] Pagination implemented for list endpoints
- [ ] Sorting and filtering query parameters supported
- [ ] HTTP status codes correct (200, 201, 204, 400, 401, 404, 422)
- [ ] Error responses follow consistent format
- [ ] Type hints on all parameters and return values

## References

- **API Spec**: `@specs/api/rest-endpoints.md` for complete endpoint definitions
- **Database Schema**: `@specs/database/schema.md` for SQLModel models
- **Endpoint Patterns**: `references/endpoint-patterns.md` for advanced patterns
