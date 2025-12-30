# CLI Error Handling Skill

This skill provides patterns and templates for implementing error handling in the CLI Todo application. Use this skill when implementing exception handling, user-friendly error messages, and graceful error recovery.

## When to Use This Skill

Use this skill when implementing:
- Command-level exception handling
- User-friendly error messages
- Graceful recovery from invalid inputs
- Logging and error reporting
- Input validation with error feedback

## Error Handling Patterns

### Command-Level Error Handling
```python
from rich.console import Console
import typer

console = Console()

@app.command()
def add_task(title: str, description: str = ""):
    """Add a new task with error handling."""
    try:
        # Validate inputs
        if not title or len(title.strip()) == 0:
            raise ValueError("Title cannot be empty")
        if len(title) > 100:
            raise ValueError("Title must be 1-100 characters")
        if len(description) > 500:
            raise ValueError("Description must be 0-500 characters")

        # Call service
        task = task_service.add_task(title=title.strip(), description=description)
        console.print(f"[green]✓ Task '{task.title}' added successfully![/green]")

    except ValueError as e:
        console.print(f"[red]✗ Input Error: {str(e)}[/red]")
    except Exception as e:
        console.print(f"[red]✗ Error adding task: {str(e)}[/red]")
```

### Service Layer Error Handling
```python
def safe_service_call(service_method, *args, **kwargs):
    """Execute service method with error handling."""
    try:
        return service_method(*args, **kwargs)
    except ValueError as e:
        console.print(f"[red]✗ Validation Error: {str(e)}[/red]")
        return None
    except KeyError as e:
        console.print(f"[red]✗ Task not found: {str(e)}[/red]")
        return None
    except Exception as e:
        console.print(f"[red]✗ Service Error: {str(e)}[/red]")
        return None
```

## Custom Exception Classes

### Application-Specific Exceptions
```python
class TaskNotFoundError(Exception):
    """Raised when a task is not found."""
    def __init__(self, task_id: int):
        self.task_id = task_id
        super().__init__(f"Task with ID {task_id} not found")

class TaskValidationError(Exception):
    """Raised when task validation fails."""
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"Validation error in {field}: {message}")

class TaskStorageError(Exception):
    """Raised when storage operations fail."""
    def __init__(self, operation: str, message: str):
        self.operation = operation
        super().__init__(f"Storage {operation} failed: {message}")
```

### Using Custom Exceptions
```python
@app.command()
def update_task(task_id: int, title: str, description: str = ""):
    """Update task with custom exception handling."""
    try:
        # Call service
        updated_task = task_service.update_task(
            task_id=task_id,
            title=title,
            description=description,
            completed=None  # Don't change completion status
        )
        console.print(f"[green]✓ Task {updated_task.id} updated successfully![/green]")

    except TaskNotFoundError:
        console.print(f"[red]✗ Task with ID {task_id} does not exist[/red]")
    except TaskValidationError as e:
        console.print(f"[red]✗ Validation Error: {e.message}[/red]")
    except Exception as e:
        console.print(f"[red]✗ Error updating task: {str(e)}[/red]")
```

## Input Validation Error Handling

### Validation with Specific Error Messages
```python
def validate_task_input(title: str, description: str = "") -> tuple[str, str]:
    """Validate task input with specific error messages."""
    if not title or len(title.strip()) == 0:
        raise TaskValidationError("title", "Title cannot be empty")

    if len(title.strip()) > 100:
        raise TaskValidationError("title", "Title must be 1-100 characters")

    if len(description) > 500:
        raise TaskValidationError("description", "Description must be 0-500 characters")

    return title.strip(), description.strip()
```

### Command with Validation
```python
@app.command()
def add_task(title: str, description: str = ""):
    """Add task with validation error handling."""
    try:
        validated_title, validated_description = validate_task_input(title, description)

        task = task_service.add_task(
            title=validated_title,
            description=validated_description
        )
        console.print(f"[green]✓ Task '{task.title}' added successfully![/green]")

    except TaskValidationError as e:
        console.print(f"[red]✗ Input Error: {e.message}[/red]")
    except Exception as e:
        console.print(f"[red]✗ Error adding task: {str(e)}[/red]")
```

## Interactive Menu Error Handling

### Menu Operation Error Handling
```python
def safe_menu_operation(operation, error_message):
    """Execute menu operation with error handling."""
    try:
        return operation()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        return None
    except TaskNotFoundError as e:
        console.print(f"[red]✗ {error_message}: Task ID {e.task_id} not found[/red]")
        return None
    except TaskValidationError as e:
        console.print(f"[red]✗ {error_message}: {e.message}[/red]")
        return None
    except Exception as e:
        console.print(f"[red]✗ {error_message}: {str(e)}[/red]")
        return None
```

### Safe Interactive Operations
```python
def interactive_delete_task():
    """Interactive delete with error handling."""
    def delete_operation():
        tasks = task_service.get_all_tasks()
        if not tasks:
            console.print("[yellow]No tasks available to delete.[/yellow]")
            return

        display_tasks(tasks)

        task_id = int(Prompt.ask("Enter task ID to delete"))

        confirm = Prompt.ask(
            f"Are you sure you want to delete task ID {task_id}? (y/N)",
            choices=["y", "n"],
            default="n"
        )

        if confirm.lower() == "y":
            result = task_service.delete_task(task_id)
            if result:
                console.print(f"[green]✓ Task {task_id} deleted successfully![/green]")
            else:
                console.print(f"[red]Task {task_id} not found.[/red]")
        else:
            console.print("[yellow]Deletion cancelled.[/yellow]")

    safe_menu_operation(delete_operation, "Error deleting task")
```

## Error Recovery Patterns

### Graceful Degradation
```python
def get_tasks_safe():
    """Get tasks with error recovery."""
    try:
        return task_service.get_all_tasks()
    except Exception as e:
        console.print(f"[red]Error loading tasks: {str(e)}[/red]")
        console.print("[yellow]Showing empty task list.[/yellow]")
        return []
```

### Fallback Values
```python
def get_task_with_fallback(task_id: int):
    """Get task with fallback error handling."""
    try:
        return task_service.get_task(task_id)
    except TaskNotFoundError:
        return None
    except Exception as e:
        console.print(f"[red]Error retrieving task: {str(e)}[/red]")
        return None
```

## Logging and Error Reporting

### Error Logging
```python
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('todo_app.log'),
        logging.StreamHandler()
    ]
)

def log_error(operation: str, error: Exception):
    """Log error with context."""
    logging.error(f"Operation: {operation}, Error: {str(error)}, Time: {datetime.now()}")
```

### Enhanced Error Handling with Logging
```python
@app.command()
def list_tasks():
    """List tasks with error logging."""
    try:
        tasks = task_service.get_all_tasks()
        display_tasks(tasks)
    except Exception as e:
        log_error("list_tasks", e)
        console.print(f"[red]✗ Error listing tasks: {str(e)}[/red]")
        # Provide fallback
        console.print("[yellow]No tasks to display.[/yellow]")
```

## Error Message Formatting

### Consistent Error Message Format
```python
def format_error_message(error_type: str, message: str) -> str:
    """Format error message consistently."""
    return f"[red]✗ {error_type}: {message}[/red]"

def display_error(error_type: str, message: str):
    """Display formatted error message."""
    console.print(format_error_message(error_type, message))

def display_validation_error(field: str, message: str):
    """Display validation error."""
    display_error("Validation Error", f"{field}: {message}")

def display_service_error(message: str):
    """Display service error."""
    display_error("Service Error", message)
```

## Error Handling in Different Contexts

### Typer Command Error Handling
```python
@app.command()
def toggle_task(task_id: int):
    """Toggle task completion with error handling."""
    try:
        if task_id <= 0:
            raise TaskValidationError("task_id", "Task ID must be positive")

        updated_task = task_service.toggle_task_completion(task_id)
        status = "completed" if updated_task.completed else "pending"
        console.print(f"[green]✓ Task {updated_task.id} marked as {status}![/green]")

    except TaskValidationError as e:
        display_validation_error(e.field, e.message)
    except TaskNotFoundError:
        display_error("Task Not Found", f"Task with ID {task_id} does not exist")
    except Exception as e:
        display_service_error(str(e))
```

### Interactive Menu Error Handling
```python
def interactive_task_operation(task_id: int, operation_name: str, operation_func):
    """Generic interactive task operation with error handling."""
    try:
        if task_id <= 0:
            console.print("[red]✗ Invalid task ID: must be positive[/red]")
            return

        result = operation_func(task_id)
        if result:
            console.print(f"[green]✓ {operation_name} completed successfully![/green]")
        else:
            console.print(f"[red]✗ {operation_name} failed: Task not found[/red]")

    except TaskNotFoundError:
        console.print(f"[red]✗ {operation_name} failed: Task not found[/red]")
    except Exception as e:
        console.print(f"[red]✗ {operation_name} failed: {str(e)}[/red]")
```

## Testing Error Handling

### Error Handling Tests
```python
import pytest
from typer.testing import CliRunner

def test_add_task_validation_error():
    """Test error handling for validation errors."""
    runner = CliRunner()

    # Test empty title
    result = runner.invoke(app, ["add", ""])
    assert result.exit_code != 0
    assert "Validation Error" in result.stdout

def test_task_not_found_error():
    """Test error handling for task not found."""
    runner = CliRunner()

    # Test invalid task ID
    result = runner.invoke(app, ["update", "999", "Updated Title"])
    assert result.exit_code != 0
    assert "not found" in result.stdout.lower()
```

### Exception Testing
```python
def test_service_error_handling(monkeypatch):
    """Test service error handling."""
    def mock_service_error(*args, **kwargs):
        raise Exception("Service unavailable")

    monkeypatch.setattr("todo.services.task_service.add_task", mock_service_error)

    runner = CliRunner()
    result = runner.invoke(app, ["add", "Test Task"])
    assert "Error" in result.stdout
    assert result.exit_code != 0
```

## Best Practices

### Error Handling Principles
- Never let unhandled exceptions crash the application
- Provide user-friendly error messages
- Log errors for debugging purposes
- Fail gracefully without losing data
- Validate inputs early in the process

### Error Message Guidelines
- Be specific about what went wrong
- Suggest possible solutions when applicable
- Use consistent formatting and color coding
- Don't expose internal implementation details
- Keep messages concise but informative
- Distinguish between user errors and system errors