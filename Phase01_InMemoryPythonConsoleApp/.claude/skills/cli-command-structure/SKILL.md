# CLI Command Structure Skill

This skill provides patterns and templates for implementing CLI command structures using the Typer framework for the Todo application. Use this skill when designing command organization, argument parsing, and command-line interface patterns.

## When to Use This Skill

Use this skill when implementing:
- Main CLI application structure with Typer
- Individual command functions with proper arguments and options
- Command argument validation and type hints
- Command help text and documentation
- Subcommand organization

## Command Structure Patterns

### Basic Command Pattern
```python
import typer

app = typer.Typer()

@app.command()
def add_task(title: str, description: str = ""):
    """Add a new task with optional description."""
    # Implementation here
    pass
```

### Command with Options
```python
@app.command()
def list_tasks(
    completed: bool = typer.Option(None, "--completed", help="Show only completed tasks"),
    all_tasks: bool = typer.Option(False, "--all", help="Show all tasks including completed")
):
    """List tasks with optional filters."""
    # Implementation here
    pass
```

### Command with Arguments Validation
```python
@app.command()
def update_task(
    task_id: int = typer.Argument(..., min=1, help="Task ID to update"),
    title: str = typer.Argument(..., help="New task title"),
    description: str = typer.Argument("", help="New task description")
):
    """Update an existing task."""
    # Implementation here
    pass
```

## Typer Best Practices

### Type Hints and Validation
- Always use proper type hints for parameters
- Use `typer.Argument(...)` for required arguments
- Use `typer.Option(...)` for optional parameters
- Apply validation constraints (min, max, regex, etc.)

### Help Text
- Write clear, concise help text for each command
- Document argument purposes in help strings
- Use consistent terminology across commands

### Error Handling in Commands
```python
@app.command()
def delete_task(task_id: int):
    """Delete a task by ID."""
    try:
        result = task_service.delete_task(task_id)
        if result:
            console.print(f"[green]Task {task_id} deleted successfully[/green]")
        else:
            console.print(f"[red]Task {task_id} not found[/red]")
    except Exception as e:
        console.print(f"[red]Error deleting task: {str(e)}[/red]")
```

## Command Organization

### Command File Structure
```
src/todo/cli/commands/
├── add.py      # add_task command
├── list.py     # list_tasks command
├── update.py   # update_task command
├── delete.py   # delete_task command
└── toggle.py   # toggle_task command
```

### Import Pattern
```python
# In main.py
from todo.cli.commands.add import add_task
from todo.cli.commands.list import list_tasks
from todo.cli.commands.update import update_task
from todo.cli.commands.delete import delete_task
from todo.cli.commands.toggle import toggle_task

app = typer.Typer()
app.command()(add_task)
app.command()(list_tasks)
app.command()(update_task)
app.command()(delete_task)
app.command()(toggle_task)
```

## Testing Command Structure

### Command Test Template
```python
import pytest
from typer.testing import CliRunner
from main import app

runner = CliRunner()

def test_add_task_command():
    """Test the add task command."""
    result = runner.invoke(app, ["add", "Test task"])
    assert result.exit_code == 0
    assert "Task added" in result.stdout

def test_list_tasks_command():
    """Test the list tasks command."""
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "ID" in result.stdout
```

## Interactive Menu Command Pattern

```python
@app.command()
def menu():
    """Launch interactive menu system."""
    while True:
        console.print("\n[bold]Todo App Menu[/bold]")
        console.print("1. Add Task")
        console.print("2. List Tasks")
        console.print("3. Update Task")
        console.print("4. Delete Task")
        console.print("5. Toggle Task")
        console.print("6. Quit")

        choice = Prompt.ask("Choose an option", choices=["1", "2", "3", "4", "5", "6"])

        if choice == "1":
            # Handle add task
            pass
        elif choice == "6":
            break
```

## Command Documentation Standards

Each command should include:
- Clear function docstring describing purpose
- Type hints for all parameters
- Proper help text for arguments and options
- Example usage in docstring if complex