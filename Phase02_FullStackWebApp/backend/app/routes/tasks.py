from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, and_, or_
from typing import List, Optional
from app.database import get_session
from app.models.task import Task, TaskCreate, TaskRead, TaskUpdate, TaskToggleComplete, Priority, RecurrencePattern
from app.models.user import User
from app.middleware.auth import get_current_user, verify_user_access
from uuid import UUID
import uuid

router = APIRouter()

@router.get("/{user_id}/tasks", response_model=List[TaskRead], summary="List all tasks", description="Retrieve all tasks for the authenticated user with optional filtering, sorting, and pagination support.")
async def get_tasks(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
    status: Optional[str] = Query(None, description="Filter tasks by status (e.g., 'todo', 'completed')"),
    priority: Optional[Priority] = Query(None, description="Filter tasks by priority level (high, medium, low, none)"),
    due_date: Optional[str] = Query(None, description="Filter tasks by due date (ISO 8601 format: YYYY-MM-DD)"),
    search: Optional[str] = Query(None, description="Search tasks by keyword in title or description"),
    sort: str = Query("created_date", description="Sort field: created_date, due_date, priority, or title"),
    order: str = Query("asc", description="Sort order: asc (ascending) or desc (descending)"),
    page: int = Query(1, description="Page number for pagination (starts at 1)", ge=1),
    limit: int = Query(50, description="Number of tasks per page (max 200)", ge=1, le=200)
):
    """
    Get all tasks for a user with optional filters and pagination.

    **Parameters:**
    - **user_id**: The UUID of the user (must match authenticated user)
    - **status**: Optional filter by task status
    - **priority**: Optional filter by priority level
    - **due_date**: Optional filter by specific due date
    - **search**: Optional text search in title/description
    - **sort**: Field to sort results by (default: created_date)
    - **order**: Sort direction (default: asc)
    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 50, max: 200)

    **Returns:**
    - List of tasks matching the criteria

    **Example:**
    ```
    GET /api/123e4567-e89b-12d3-a456-426614174000/tasks?priority=high&status=todo&sort=due_date&order=asc&page=1&limit=20
    ```
    """
    # Verify user access
    if current_user.get("sub") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access these tasks"
        )

    # Build query
    query = select(Task).where(Task.user_id == uuid.UUID(user_id))

    # Apply filters
    if status:
        query = query.where(Task.status == status)
    if priority:
        query = query.where(Task.priority == priority)
    if due_date:
        from datetime import datetime
        due_date_obj = datetime.fromisoformat(due_date)
        query = query.where(Task.due_date == due_date_obj)
    if search:
        query = query.where(
            or_(
                Task.title.contains(search),
                Task.description.contains(search) if Task.description else False
            )
        )

    # Apply sorting
    if sort == "due_date":
        if order == "desc":
            query = query.order_by(Task.due_date.desc())
        else:
            query = query.order_by(Task.due_date.asc())
    elif sort == "priority":
        if order == "desc":
            query = query.order_by(Task.priority.desc())
        else:
            query = query.order_by(Task.priority.asc())
    elif sort == "title":
        if order == "desc":
            query = query.order_by(Task.title.desc())
        else:
            query = query.order_by(Task.title.asc())
    else:  # created_date
        if order == "desc":
            query = query.order_by(Task.created_at.desc())
        else:
            query = query.order_by(Task.created_at.asc())

    # Apply pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)

    tasks = session.exec(query).all()
    return [TaskRead.model_validate(task) for task in tasks]


@router.post("/{user_id}/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED, summary="Create a new task", description="Create a new task for the authenticated user with optional priority, due date, tags, and recurrence pattern.")
async def create_task(
    user_id: str,
    task: TaskCreate,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Create a new task for a user.

    **Parameters:**
    - **user_id**: The UUID of the user (must match authenticated user)
    - **task**: TaskCreate object containing:
      - title (required): Task title (1-255 characters)
      - description (optional): Task description (max 1000 characters)
      - priority (optional): Task priority (high, medium, low, none; default: none)
      - due_date (optional): Due date/time for the task (ISO 8601 format)
      - recurrence_pattern (optional): Recurrence pattern (daily, weekly, monthly, yearly; default: none)
      - tags (optional): List of tags for organization

    **Returns:**
    - TaskRead object with the created task details

    **Example:**
    ```
    POST /api/123e4567-e89b-12d3-a456-426614174000/tasks
    {
      "title": "Complete project documentation",
      "description": "Write comprehensive documentation for the new feature",
      "priority": "high",
      "due_date": "2026-01-15T17:00:00",
      "recurrence_pattern": "none",
      "tags": ["documentation", "urgent"]
    }
    ```

    **Status Codes:**
    - 201: Task created successfully
    - 401: Unauthorized (invalid or missing JWT token)
    - 403: Forbidden (user_id doesn't match authenticated user)
    - 404: User not found
    - 422: Validation error in request body
    """
    # Verify user access
    if current_user.get("sub") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create tasks for this user"
        )

    # Validate user exists
    user = session.get(User, uuid.UUID(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Create task
    db_task = Task(
        title=task.title,
        description=task.description,
        status="todo",  # Default status
        priority=task.priority,
        due_date=task.due_date,
        recurrence_pattern=task.recurrence_pattern,
        user_id=uuid.UUID(user_id),
        tags=task.tags
    )
    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    return TaskRead.model_validate(db_task)


@router.get("/{user_id}/tasks/{task_id}", response_model=TaskRead, summary="Get a specific task", description="Retrieve detailed information about a specific task by ID.")
async def get_task(
    user_id: str,
    task_id: str,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get a specific task by ID.

    **Parameters:**
    - **user_id**: The UUID of the user (must match authenticated user)
    - **task_id**: The UUID of the task to retrieve

    **Returns:**
    - TaskRead object with complete task details

    **Example:**
    ```
    GET /api/123e4567-e89b-12d3-a456-426614174000/tasks/987e6543-e21c-43d2-b765-432614174999
    ```

    **Status Codes:**
    - 200: Task found and returned
    - 401: Unauthorized (invalid or missing JWT token)
    - 403: Forbidden (user_id doesn't match authenticated user or task owner)
    - 404: Task not found
    """
    # Verify user access
    if current_user.get("sub") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this task"
        )

    # Get task
    task = session.get(Task, uuid.UUID(task_id))
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    if str(task.user_id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this task"
        )

    return TaskRead.model_validate(task)


@router.put("/{user_id}/tasks/{task_id}", response_model=TaskRead, summary="Update a task", description="Update an existing task with new values for title, description, priority, due date, recurrence pattern, or tags.")
async def update_task(
    user_id: str,
    task_id: str,
    task_update: TaskUpdate,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update a specific task.

    **Parameters:**
    - **user_id**: The UUID of the user (must match authenticated user)
    - **task_id**: The UUID of the task to update
    - **task_update**: TaskUpdate object with optional fields to update:
      - title: New task title (1-255 characters)
      - description: New task description (max 1000 characters)
      - status: New task status ('todo' or 'completed')
      - priority: New task priority (high, medium, low, none)
      - due_date: New due date/time (ISO 8601 format)
      - recurrence_pattern: New recurrence pattern (daily, weekly, monthly, yearly)
      - tags: Updated list of tags

    **Returns:**
    - TaskRead object with updated task details

    **Example:**
    ```
    PUT /api/123e4567-e89b-12d3-a456-426614174000/tasks/987e6543-e21c-43d2-b765-432614174999
    {
      "title": "Updated task title",
      "priority": "medium",
      "due_date": "2026-01-20T17:00:00"
    }
    ```

    **Status Codes:**
    - 200: Task updated successfully
    - 401: Unauthorized (invalid or missing JWT token)
    - 403: Forbidden (user_id doesn't match authenticated user or task owner)
    - 404: Task not found
    - 422: Validation error in request body
    """
    # Verify user access
    if current_user.get("sub") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this task"
        )

    # Get task
    db_task = session.get(Task, uuid.UUID(task_id))
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    if str(db_task.user_id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this task"
        )

    # Update task fields
    update_data = task_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)

    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    return TaskRead.model_validate(db_task)


@router.delete("/{user_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a task", description="Permanently delete a task by ID. This action cannot be undone.")
async def delete_task(
    user_id: str,
    task_id: str,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete a specific task permanently.

    **Parameters:**
    - **user_id**: The UUID of the user (must match authenticated user)
    - **task_id**: The UUID of the task to delete

    **Returns:**
    - No content (204 No Content) on successful deletion

    **Example:**
    ```
    DELETE /api/123e4567-e89b-12d3-a456-426614174000/tasks/987e6543-e21c-43d2-b765-432614174999
    ```

    **Status Codes:**
    - 204: Task deleted successfully
    - 401: Unauthorized (invalid or missing JWT token)
    - 403: Forbidden (user_id doesn't match authenticated user or task owner)
    - 404: Task not found

    **Warning:**
    This action is irreversible. The task will be permanently removed from the database.
    """
    # Verify user access
    if current_user.get("sub") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this task"
        )

    # Get task
    db_task = session.get(Task, uuid.UUID(task_id))
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    if str(db_task.user_id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this task"
        )

    session.delete(db_task)
    session.commit()


@router.patch("/{user_id}/tasks/{task_id}/complete", response_model=TaskRead, summary="Toggle task completion", description="Mark a task as completed or incomplete. For recurring tasks, marking as complete automatically creates a new instance for the next recurrence period.")
async def toggle_task_completion(
    user_id: str,
    task_id: str,
    completion_data: TaskToggleComplete,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Toggle task completion status with automatic recurring task rescheduling.

    **Parameters:**
    - **user_id**: The UUID of the user (must match authenticated user)
    - **task_id**: The UUID of the task to toggle
    - **completion_data**: TaskToggleComplete object with:
      - completed (boolean): True to mark as complete, False to mark as incomplete

    **Behavior:**
    - When completed=True:
      - Task status changes to 'completed'
      - completed_at timestamp is set
      - If task has a recurrence pattern, a new task instance is automatically created for the next period
    - When completed=False:
      - Task status changes back to 'todo'
      - completed_at timestamp is cleared

    **Recurring Task Schedule:**
    - daily: New task due tomorrow
    - weekly: New task due next week
    - monthly: New task due in ~30 days
    - yearly: New task due in ~365 days

    **Returns:**
    - TaskRead object with updated task details

    **Example:**
    ```
    PATCH /api/123e4567-e89b-12d3-a456-426614174000/tasks/987e6543-e21c-43d2-b765-432614174999/complete
    {
      "completed": true
    }
    ```

    **Status Codes:**
    - 200: Task completion toggled successfully
    - 401: Unauthorized (invalid or missing JWT token)
    - 403: Forbidden (user_id doesn't match authenticated user or task owner)
    - 404: Task not found
    - 422: Validation error in request body
    """
    from datetime import datetime, timedelta

    # Verify user access
    if current_user.get("sub") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this task"
        )

    # Get task
    db_task = session.get(Task, uuid.UUID(task_id))
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    if str(db_task.user_id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this task"
        )

    # Update completion status
    if completion_data.completed:
        db_task.status = "completed"
        db_task.completed_at = datetime.utcnow()

        # Handle recurring tasks - create new instance
        if db_task.recurrence_pattern and db_task.recurrence_pattern != RecurrencePattern.NONE:
            # Calculate next due date
            next_due_date = None
            if db_task.due_date:
                current_due = db_task.due_date
                if db_task.recurrence_pattern == RecurrencePattern.DAILY:
                    next_due_date = current_due + timedelta(days=1)
                elif db_task.recurrence_pattern == RecurrencePattern.WEEKLY:
                    next_due_date = current_due + timedelta(weeks=1)
                elif db_task.recurrence_pattern == RecurrencePattern.MONTHLY:
                    # Add approximately 30 days for monthly
                    next_due_date = current_due + timedelta(days=30)
                elif db_task.recurrence_pattern == RecurrencePattern.YEARLY:
                    # Add approximately 365 days for yearly
                    next_due_date = current_due + timedelta(days=365)

            # Create new task instance for next occurrence
            new_recurring_task = Task(
                title=db_task.title,
                description=db_task.description,
                status="todo",
                priority=db_task.priority,
                due_date=next_due_date,
                recurrence_pattern=db_task.recurrence_pattern,
                user_id=db_task.user_id,
                tags=db_task.tags.copy() if db_task.tags else []
            )
            session.add(new_recurring_task)
    else:
        db_task.status = "todo"
        db_task.completed_at = None

    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    return TaskRead.model_validate(db_task)