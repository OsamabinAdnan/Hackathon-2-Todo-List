# CLI Input Validation Skill

This skill provides patterns and templates for implementing user input validation in the CLI Todo application. Use this skill when implementing argument validation, user input parsing, and validation feedback mechanisms.

## When to Use This Skill

Use this skill when implementing:
- Command argument validation
- User input validation in interactive menus
- Parameter checking and error handling
- Input sanitization and type conversion
- Validation error messages and user feedback

## Validation Patterns

### Command Argument Validation
```python
import typer
from typing import Optional

def validate_task_id(task_id: int) -> int:
    """Validate that task ID is positive."""
    if task_id <= 0:
        raise typer.BadParameter("Task ID must be a positive integer")
    return task_id

def validate_title(title: str) -> str:
    """Validate task title length."""
    if not title or len(title.strip()) == 0:
        raise typer.BadParameter("Title cannot be empty")
    if len(title) > 100:
        raise typer.BadParameter("Title must be 1-100 characters")
    return title.strip()

@app.command()
def update_task(
    task_id: int = typer.Argument(..., callback=validate_task_id),
    title: str = typer.Argument(..., callback=validate_title),
    description: str = typer.Argument("", help="Task description (max 500 chars)")
):
    """Update a task with validation."""
    if description and len(description) > 500:
        raise typer.BadParameter("Description must be 0-500 characters")

    # Update task implementation
    pass
```

### Custom Validation Callbacks
```python
def validate_priority(priority: str) -> str:
    """Validate priority value."""
    valid_priorities = ["low", "medium", "high", "critical"]
    if priority.lower() not in valid_priorities:
        raise typer.BadParameter(f"Priority must be one of: {', '.join(valid_priorities)}")
    return priority.lower()
```

### Type Conversion with Validation
```python
def validate_and_convert_date(date_str: str) -> datetime:
    """Validate and convert date string."""
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except ValueError:
        raise typer.BadParameter("Date must be in ISO format (YYYY-MM-DD)")
```

## Interactive Input Validation

### Using Rich Prompts with Validation
```python
from rich.prompt import Prompt, IntPrompt

def get_valid_task_id() -> int:
    """Get a valid task ID from user."""
    while True:
        try:
            task_id = IntPrompt.ask("Enter task ID", default=1)
            if task_id > 0:
                return task_id
            else:
                console.print("[red]Task ID must be positive[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")

def get_valid_title() -> str:
    """Get a valid task title from user."""
    while True:
        title = Prompt.ask("Enter task title (1-100 chars)")
        if 1 <= len(title) <= 100:
            return title
        else:
            console.print("[red]Title must be 1-100 characters[/red]")
```

### Menu Input Validation
```python
def get_menu_choice() -> str:
    """Get valid menu choice from user."""
    valid_choices = ["1", "2", "3", "4", "5", "6"]
    while True:
        choice = Prompt.ask("Choose an option", choices=valid_choices)
        if choice in valid_choices:
            return choice
        else:
            console.print("[red]Invalid choice. Please select 1-6.[/red]")
```

## Validation in Interactive Menu Context

### Input Validation with Error Recovery
```python
def interactive_add_task():
    """Interactive task addition with validation."""
    try:
        title = get_valid_title()

        description = Prompt.ask("Enter task description (optional, max 500 chars)", default="")
        if len(description) > 500:
            console.print("[red]Description too long. Truncated to 500 characters.[/red]")
            description = description[:500]

        # Add task to service
        task = task_service.add_task(title=title, description=description)
        console.print(f"[green]Task '{task.title}' added successfully![/green]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled[/yellow]")
    except Exception as e:
        console.print(f"[red]Error adding task: {str(e)}[/red]")
```

## Validation Error Handling

### Custom Exception Handling
```python
class ValidationError(Exception):
    """Custom validation exception."""
    pass

def safe_validate_and_execute(validation_func, execution_func, error_message):
    """Execute function with validation and error handling."""
    try:
        validated_input = validation_func()
        return execution_func(validated_input)
    except ValidationError as e:
        console.print(f"[red]{error_message}: {str(e)}[/red]")
        return None
    except Exception as e:
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
        return None
```

### Input Sanitization
```python
import re

def sanitize_input(text: str) -> str:
    """Sanitize user input by removing potentially harmful characters."""
    # Remove potentially harmful characters
    sanitized = re.sub(r'[<>"\']', '', text)
    return sanitized.strip()
```

## Validation Testing Patterns

### Unit Testing Validation
```python
import pytest
from typer.testing import CliRunner

def test_add_task_validation():
    """Test validation in add task command."""
    runner = CliRunner()

    # Test empty title
    result = runner.invoke(app, ["add", ""])
    assert result.exit_code != 0
    assert "Title cannot be empty" in result.stdout

    # Test long title
    long_title = "a" * 101
    result = runner.invoke(app, ["add", long_title])
    assert result.exit_code != 0
    assert "Title must be 1-100 characters" in result.stdout
```

### Interactive Validation Testing
```python
def test_interactive_input_validation(monkeypatch):
    """Test interactive input validation."""
    # Mock user input for validation
    inputs = iter(["", "a" * 101, "Valid Title"])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    title = get_valid_title()
    assert title == "Valid Title"
```

## Best Practices

### Validation Principles
- Validate input as early as possible
- Provide clear, actionable error messages
- Use consistent validation across the application
- Never trust user input - always validate
- Fail fast when validation fails

### Error Message Guidelines
- Be specific about what went wrong
- Include expected format when applicable
- Suggest valid alternatives when possible
- Use consistent color coding (red for errors)
- Keep messages concise but informative