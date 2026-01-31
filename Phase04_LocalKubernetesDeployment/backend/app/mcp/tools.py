"""
Tools for task management.
Wraps existing task service logic for AI agent consumption.
Following the colleague's approach without MCP decorators.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlmodel import Session, select
import logging
from app.models.task import Task
from app.models.user import User
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

def _find_task_by_identifier(session: Session, user_id: UUID, task_identifier: str) -> Optional[Task]:
    """Helper to find task by ID or fuzzy title match."""
    # Try as UUID first
    try:
        task_id = UUID(task_identifier)
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        task = session.exec(statement).first()
        return task
    except ValueError:
        pass

    # Fuzzy match by title
    statement = select(Task).where(Task.user_id == user_id)
    tasks = session.exec(statement).all()
    matches = [t for t in tasks if task_identifier.lower() in t.title.lower()]

    if len(matches) == 1:
        return matches[0]
    return None


def _find_tasks_by_identifier(session: Session, user_id: UUID, task_identifier: str) -> List[Task]:
    """Helper to find all tasks by ID or fuzzy title match."""
    # Try as UUID first (single task)
    try:
        task_id = UUID(task_identifier)
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        task = session.exec(statement).first()
        if task:
            return [task]
        return []
    except ValueError:
        pass

    # Fuzzy match by title (multiple tasks possible)
    statement = select(Task).where(Task.user_id == user_id)
    tasks = session.exec(statement).all()
    matches = [t for t in tasks if task_identifier.lower() in t.title.lower()]

    return matches

def add_task(
    session: Session,
    user_id: str,  # Changed to string to match our UUID handling
    title: str,
    description: Optional[str] = None,
    priority: Optional[str] = "none",
    due_date: Optional[str] = None,
    tags: Optional[List[str]] = None,
    recurrence_pattern: Optional[str] = "none"
) -> Dict[str, Any]:
    """
    Create a new task.
    """
    logger.info(f"Tool: add_task called for user {user_id} with title='{title}', priority='{priority}', due_date='{due_date}', tags='{tags}', recurrence_pattern='{recurrence_pattern}'")
    try:
        # Convert user_id to UUID
        user_uuid = uuid.UUID(user_id)

        # Validate user exists
        user = session.get(User, user_uuid)
        if not user:
            return {"success": False, "message": "User not found"}

        # Parse due_date if provided
        parsed_due_date = None
        if due_date:
            # Handle different date/time formats
            date_str = due_date.strip()

            # Handle "today" and relative dates
            if date_str.lower() == 'today':
                from datetime import date
                today = date.today()
                parsed_due_date = datetime.combine(today, datetime.min.time())
            elif 'today at' in date_str.lower():
                # Parse "today at HH:MM AM/PM"
                import re
                today_match = re.search(r'today at (\d{1,2}):(\d{2})\s*(AM|PM|am|pm)', date_str, re.IGNORECASE)
                if today_match:
                    from datetime import date
                    hour, minute, period = today_match.groups()
                    hour = int(hour)
                    minute = int(minute)

                    # Convert 12-hour to 24-hour format
                    if period.upper() == 'PM' and hour != 12:
                        hour += 12
                    elif period.upper() == 'AM' and hour == 12:
                        hour = 0

                    today = date.today()
                    parsed_due_date = datetime.combine(today, datetime.min.time().replace(hour=hour, minute=minute))
            elif 'tomorrow' in date_str.lower():
                from datetime import date, timedelta
                tomorrow = date.today() + timedelta(days=1)
                parsed_due_date = datetime.combine(tomorrow, datetime.min.time())
            else:
                try:
                    # Try ISO format first
                    parsed_due_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                except ValueError:
                    try:
                        # Try YYYY-MM-DD format
                        parsed_due_date = datetime.strptime(date_str, '%Y-%m-%d')
                    except ValueError:
                        try:
                            # Try DD/MM/YYYY or MM/DD/YYYY format
                            parsed_due_date = datetime.strptime(date_str, '%d/%m/%Y')
                        except ValueError:
                            try:
                                # Try DD-MM-YYYY or MM-DD-YYYY format
                                parsed_due_date = datetime.strptime(date_str, '%d-%m-%Y')
                            except ValueError:
                                logger.warning(f"Could not parse due_date: {date_str}")
                                parsed_due_date = None

        # Create the task
        task = Task(
            user_id=user_uuid,
            title=title,
            description=description,
            status="todo",
            priority=priority.lower() if priority else "none",
            tags=tags or [],
            due_date=parsed_due_date,
            recurrence_pattern=recurrence_pattern.lower() if recurrence_pattern else "none",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        session.add(task)
        session.commit()
        session.refresh(task)

        return {
            "success": True,
            "message": f"Task '{task.title}' created successfully.",
            "task": {
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "is_completed": task.status == "completed"
            }
        }
    except Exception as e:
        return {"success": False, "message": f"Failed to create task: {str(e)}"}

def list_tasks(
    session: Session,
    user_id: str,  # Changed to string
    status: Optional[str] = "all",  # Filter by status (all, pending, completed)
    priority: Optional[str] = None,  # Filter by priority (high, medium, low, none)
    due_date: Optional[str] = None  # Filter by due date (today, tomorrow, this_week, this_month, YYYY-MM-DD)
) -> Dict[str, Any]:
    """
    List all tasks for the user.
    """
    logger.info(f"Tool: list_tasks called for user {user_id} with status={status}, priority={priority}, due_date={due_date}")
    try:
        # Convert user_id to UUID
        user_uuid = uuid.UUID(user_id)

        # Validate user exists
        user = session.get(User, user_uuid)
        if not user:
            return {"success": False, "message": "User not found", "tasks": [], "count": 0}

        # Build query based on filters
        query = select(Task).where(Task.user_id == user_uuid)

        # Apply status filter
        if status == "pending":
            query = query.where(Task.status == "todo")
        elif status == "completed":
            query = query.where(Task.status == "completed")

        # Apply priority filter
        if priority:
            query = query.where(Task.priority == priority.lower())

        # Apply due date filter
        if due_date:
            from datetime import datetime, date, timedelta
            if due_date.lower() == "today":
                today_start = datetime.combine(date.today(), datetime.min.time())
                today_end = datetime.combine(date.today(), datetime.max.time())
                query = query.where(Task.due_date >= today_start, Task.due_date <= today_end)
            elif due_date.lower() == "tomorrow":
                tomorrow = date.today() + timedelta(days=1)
                tomorrow_start = datetime.combine(tomorrow, datetime.min.time())
                tomorrow_end = datetime.combine(tomorrow, datetime.max.time())
                query = query.where(Task.due_date >= tomorrow_start, Task.due_date <= tomorrow_end)
            elif due_date.lower() == "this_week":
                from datetime import datetime, timedelta
                today = date.today()
                start_of_week = today - timedelta(days=today.weekday())
                end_of_week = start_of_week + timedelta(days=6)
                start_datetime = datetime.combine(start_of_week, datetime.min.time())
                end_datetime = datetime.combine(end_of_week, datetime.max.time())
                query = query.where(Task.due_date >= start_datetime, Task.due_date <= end_datetime)
            elif due_date.lower() == "this_month":
                from datetime import datetime
                today = date.today()
                start_of_month = today.replace(day=1)
                # Calculate end of month
                import calendar
                last_day = calendar.monthrange(today.year, today.month)[1]
                end_of_month = today.replace(day=last_day)
                start_datetime = datetime.combine(start_of_month, datetime.min.time())
                end_datetime = datetime.combine(end_of_month, datetime.max.time())
                query = query.where(Task.due_date >= start_datetime, Task.due_date <= end_datetime)
            else:
                # Try to parse as YYYY-MM-DD format
                try:
                    specific_date = datetime.strptime(due_date, '%Y-%m-%d').date()
                    specific_start = datetime.combine(specific_date, datetime.min.time())
                    specific_end = datetime.combine(specific_date, datetime.max.time())
                    query = query.where(Task.due_date >= specific_start, Task.due_date <= specific_end)
                except ValueError:
                    # Invalid date format, ignore the filter
                    pass

        tasks = session.exec(query).all()

        task_list = []
        for task in tasks:
            task_list.append({
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "is_completed": task.status == "completed",
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None
            })

        return {
            "success": True,
            "count": len(task_list),
            "tasks": task_list
        }
    except Exception as e:
        return {"success": False, "message": f"Failed to list tasks: {str(e)}"}

def complete_task(
    session: Session,
    user_id: str,  # Changed to string
    task_identifier: str,
    completed: Optional[bool] = True  # True to complete, False to mark as incomplete
) -> Dict[str, Any]:
    """
    Mark a task as completed or incomplete.
    Accepts UUID or partial title.
    For recurring tasks, when completed, creates a new instance of the task with updated due date.
    """
    logger.info(f"Tool: complete_task called for user {user_id} with task_identifier='{task_identifier}', completed={completed}")
    try:
        # Convert user_id to UUID
        user_uuid = uuid.UUID(user_id)

        task = _find_task_by_identifier(session, user_uuid, task_identifier)
        if not task:
            return {"success": False, "message": f"Task '{task_identifier}' not found or ambiguous."}

        # Update task completion status
        old_status = task.status
        task.status = "completed" if completed else "todo"
        task.completed_at = datetime.utcnow() if completed else None
        task.updated_at = datetime.utcnow()

        session.add(task)

        # Handle recurring tasks - create new instance if task is completed and has recurrence pattern
        new_task_created = False
        if completed and task.recurrence_pattern and task.recurrence_pattern != "none" and task.due_date:
            from datetime import timedelta
            # Calculate next due date based on recurrence pattern
            next_due_date = task.due_date
            if task.recurrence_pattern == "daily":
                next_due_date = task.due_date + timedelta(days=1)
            elif task.recurrence_pattern == "weekly":
                next_due_date = task.due_date + timedelta(weeks=1)
            elif task.recurrence_pattern == "monthly":
                # Add one month - handle day overflow
                year = task.due_date.year
                month = task.due_date.month + 1
                day = task.due_date.day

                # Handle year overflow
                if month > 12:
                    year += 1
                    month = 1

                # Handle day overflow (e.g., Jan 31 + 1 month should be Feb 28/29, not Mar 3)
                import calendar
                max_day = calendar.monthrange(year, month)[1]
                if day > max_day:
                    day = max_day

                next_due_date = task.due_date.replace(year=year, month=month, day=day)
            elif task.recurrence_pattern == "yearly":
                # Add one year - handle leap year edge cases
                year = task.due_date.year + 1
                month = task.due_date.month
                day = task.due_date.day

                # Handle leap year (Feb 29 -> Feb 28 in non-leap years)
                import calendar
                max_day = calendar.monthrange(year, month)[1]
                if day > max_day:
                    day = max_day

                next_due_date = task.due_date.replace(year=year, month=month, day=day)

            # Create a new task with the same properties but updated due date
            new_task = Task(
                user_id=task.user_id,
                title=task.title,
                description=task.description,
                status="todo",
                priority=task.priority,
                tags=task.tags,
                due_date=next_due_date,
                recurrence_pattern=task.recurrence_pattern,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            session.add(new_task)
            session.commit()
            session.refresh(new_task)
            new_task_created = True

        session.commit()
        session.refresh(task)

        status_text = "completed" if completed else "marked as incomplete"
        message = f"Task '{task.title}' {status_text}."
        if new_task_created and completed:
            message += f" A new recurring instance has been created with due date {next_due_date.strftime('%Y-%m-%d')}."

        return {
            "success": True,
            "message": message,
            "task": {"id": str(task.id), "is_completed": completed},
            "new_task_created": new_task_created
        }
    except Exception as e:
        return {"success": False, "message": f"Failed to update task completion status: {str(e)}"}

def update_task(
    session: Session,
    user_id: str,  # Changed to string
    task_identifier: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    tags: Optional[List[str]] = None,
    recurrence_pattern: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update a task's title, description, priority, due date, tags, or recurrence pattern.
    """
    logger.info(f"Tool: update_task called for user {user_id} with task_identifier='{task_identifier}'")
    try:
        # Convert user_id to UUID
        user_uuid = uuid.UUID(user_id)

        task = _find_task_by_identifier(session, user_uuid, task_identifier)
        if not task:
            return {"success": False, "message": f"Task '{task_identifier}' not found or ambiguous."}

        # Update task fields
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if priority is not None:
            task.priority = priority.lower() if priority else task.priority
        if due_date is not None:
            if due_date:
                # Handle different date/time formats
                date_str = due_date.strip()

                # Handle "today" and relative dates
                if date_str.lower() == 'today':
                    from datetime import date
                    today = date.today()
                    parsed_due_date = datetime.combine(today, datetime.min.time())
                elif 'today at' in date_str.lower():
                    # Parse "today at HH:MM AM/PM"
                    import re
                    today_match = re.search(r'today at (\d{1,2}):(\d{2})\s*(AM|PM|am|pm)', date_str, re.IGNORECASE)
                    if today_match:
                        from datetime import date
                        hour, minute, period = today_match.groups()
                        hour = int(hour)
                        minute = int(minute)

                        # Convert 12-hour to 24-hour format
                        if period.upper() == 'PM' and hour != 12:
                            hour += 12
                        elif period.upper() == 'AM' and hour == 12:
                            hour = 0

                        today = date.today()
                        parsed_due_date = datetime.combine(today, datetime.min.time().replace(hour=hour, minute=minute))
                elif 'tomorrow' in date_str.lower():
                    from datetime import date, timedelta
                    tomorrow = date.today() + timedelta(days=1)
                    parsed_due_date = datetime.combine(tomorrow, datetime.min.time())
                else:
                    try:
                        # Try ISO format first
                        parsed_due_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    except ValueError:
                        try:
                            # Try YYYY-MM-DD format
                            parsed_due_date = datetime.strptime(date_str, '%Y-%m-%d')
                        except ValueError:
                            try:
                                # Try DD/MM/YYYY or MM/DD/YYYY format
                                parsed_due_date = datetime.strptime(date_str, '%d/%m/%Y')
                            except ValueError:
                                try:
                                    # Try DD-MM-YYYY or MM-DD-YYYY format
                                    parsed_due_date = datetime.strptime(date_str, '%d-%m-%Y')
                                except ValueError:
                                    logger.warning(f"Could not parse due_date: {date_str}")
                                    parsed_due_date = None

                task.due_date = parsed_due_date
            else:
                task.due_date = None
        if tags is not None:
            task.tags = tags
        if recurrence_pattern is not None:
            task.recurrence_pattern = recurrence_pattern.lower() if recurrence_pattern else task.recurrence_pattern

        task.updated_at = datetime.utcnow()

        session.add(task)
        session.commit()
        session.refresh(task)

        return {
            "success": True,
            "message": f"Task '{task.title}' updated.",
            "task": {
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "tags": task.tags,
                "recurrence_pattern": task.recurrence_pattern
            }
        }
    except Exception as e:
        return {"success": False, "message": f"Failed to update task: {str(e)}"}

def delete_task(
    session: Session,
    user_id: str,  # Changed to string
    task_identifier: str,
    status: Optional[str] = None,  # Filter by status (pending, completed)
    priority: Optional[str] = None,  # Filter by priority (high, medium, low, none)
    due_date: Optional[str] = None  # Filter by due date (today, tomorrow, this_week, this_month, YYYY-MM-DD)
) -> Dict[str, Any]:
    """
    Delete a task.
    """
    logger.info(f"Tool: delete_task called for user {user_id} with task_identifier='{task_identifier}', status={status}, priority={priority}, due_date={due_date}")
    try:
        # Convert user_id to UUID
        user_uuid = uuid.UUID(user_id)

        # Check if the task_identifier is a numeric string that could represent an index
        # but first check if it's actually a UUID (full UUID format)
        is_possible_index = task_identifier.isdigit()

        # Build query based on filters
        query = select(Task).where(Task.user_id == user_uuid)

        # Apply filters
        if is_possible_index:
            # If it's a numeric identifier, try to parse as UUID first
            try:
                task_id = UUID(task_identifier)
                query = query.where(Task.id == task_id)
            except ValueError:
                # Not a valid UUID, treat as title search
                query = query.where(Task.title.ilike(f'%{task_identifier}%'))
        else:
            # Regular title search
            query = query.where(Task.title.ilike(f'%{task_identifier}%'))

        # Apply additional filters
        if status:
            if status == "pending":
                query = query.where(Task.status == "todo")
            elif status == "completed":
                query = query.where(Task.status == "completed")

        if priority:
            query = query.where(Task.priority == priority.lower())

        if due_date:
            from datetime import datetime, date, timedelta
            if due_date.lower() == "today":
                today_start = datetime.combine(date.today(), datetime.min.time())
                today_end = datetime.combine(date.today(), datetime.max.time())
                query = query.where(Task.due_date >= today_start, Task.due_date <= today_end)
            elif due_date.lower() == "tomorrow":
                tomorrow = date.today() + timedelta(days=1)
                tomorrow_start = datetime.combine(tomorrow, datetime.min.time())
                tomorrow_end = datetime.combine(tomorrow, datetime.max.time())
                query = query.where(Task.due_date >= tomorrow_start, Task.due_date <= tomorrow_end)
            elif due_date.lower() == "this_week":
                from datetime import datetime, timedelta
                today = date.today()
                start_of_week = today - timedelta(days=today.weekday())
                end_of_week = start_of_week + timedelta(days=6)
                start_datetime = datetime.combine(start_of_week, datetime.min.time())
                end_datetime = datetime.combine(end_of_week, datetime.max.time())
                query = query.where(Task.due_date >= start_datetime, Task.due_date <= end_datetime)
            elif due_date.lower() == "this_month":
                from datetime import datetime
                today = date.today()
                start_of_month = today.replace(day=1)
                # Calculate end of month
                import calendar
                last_day = calendar.monthrange(today.year, today.month)[1]
                end_of_month = today.replace(day=last_day)
                start_datetime = datetime.combine(start_of_month, datetime.min.time())
                end_datetime = datetime.combine(end_of_month, datetime.max.time())
                query = query.where(Task.due_date >= start_datetime, Task.due_date <= end_datetime)
            else:
                # Try to parse as YYYY-MM-DD format
                try:
                    specific_date = datetime.strptime(due_date, '%Y-%m-%d').date()
                    specific_start = datetime.combine(specific_date, datetime.min.time())
                    specific_end = datetime.combine(specific_date, datetime.max.time())
                    query = query.where(Task.due_date >= specific_start, Task.due_date <= specific_end)
                except ValueError:
                    # Invalid date format, ignore the filter
                    pass

        # Execute query
        tasks = session.exec(query).all()

        if len(tasks) == 0:
            # If it's a numeric identifier that doesn't match any task titles, it might be invalid
            if task_identifier.isdigit():
                return {"success": False, "message": f"No task found with ID or title matching '{task_identifier}'."}
            else:
                return {"success": False, "message": f"Task '{task_identifier}' not found with the specified filters."}
        elif len(tasks) > 1:
            # Return list of matching tasks for user selection
            task_list = []
            for i, task in enumerate(tasks, 1):
                task_info = {
                    "index": i,
                    "id": str(task.id),
                    "title": task.title,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "priority": task.priority,
                    "status": task.status
                }
                task_list.append(task_info)

            return {
                "success": False,
                "message": f"Multiple tasks found for '{task_identifier}' with the specified filters. Please specify which one to delete.",
                "tasks": task_list,
                "task_identifier": task_identifier
            }
        else:
            # Single task found, proceed with deletion
            task = tasks[0]
            session.delete(task)
            session.commit()

            return {
                "success": True,
                "message": f"Task '{task.title}' deleted."
            }
    except Exception as e:
        return {"success": False, "message": f"Failed to delete task: {str(e)}"}