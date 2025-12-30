# CLI Interactive Menu Skill

This skill provides patterns and templates for implementing interactive menu systems in the CLI Todo application. Use this skill when implementing menu navigation, user selection handling, and interactive command flows.

## When to Use This Skill

Use this skill when implementing:
- Interactive main menu system
- Navigation between different menu options
- User selection handling and input processing
- Menu state management
- Interactive command workflows

## Interactive Menu Patterns

### Basic Menu Structure
```python
from rich.prompt import Prompt
from rich.console import Console

console = Console()

def interactive_menu():
    """Main interactive menu loop."""
    while True:
        display_menu_options()

        choice = get_menu_choice()

        if choice == "1":
            interactive_add_task()
        elif choice == "2":
            interactive_list_tasks()
        elif choice == "3":
            interactive_update_task()
        elif choice == "4":
            interactive_delete_task()
        elif choice == "5":
            interactive_toggle_task()
        elif choice == "6":
            console.print("[green]Goodbye![/green]")
            break
        else:
            console.print("[red]Invalid choice. Please select 1-6.[/red]")
```

### Menu Display
```python
def display_menu_options():
    """Display menu options with rich formatting."""
    from rich.panel import Panel

    menu_text = (
        "[bold blue]1.[/bold blue] Add Task\n"
        "[bold blue]2.[/bold blue] List Tasks\n"
        "[bold blue]3.[/bold blue] Update Task\n"
        "[bold blue]4.[/bold blue] Delete Task\n"
        "[bold blue]5.[/bold blue] Toggle Task Status\n"
        "[bold blue]6.[/bold blue] Quit\n"
    )

    panel = Panel(
        menu_text,
        title="[bold green]Todo App Menu[/bold green]",
        border_style="bright_blue"
    )
    console.print(panel)
```

### Menu Choice Handling
```python
def get_menu_choice() -> str:
    """Get valid menu choice from user."""
    while True:
        try:
            choice = Prompt.ask(
                "[bold]Select an option (1-6)[/bold]",
                choices=["1", "2", "3", "4", "5", "6"],
                default="6"
            )
            return choice
        except KeyboardInterrupt:
            console.print("\n[yellow]Operation cancelled[/yellow]")
            return "6"  # Return to quit
        except Exception:
            console.print("[red]Invalid input. Please enter 1-6.[/red]")
```

## Interactive Task Operations

### Interactive Add Task
```python
def interactive_add_task():
    """Interactive task addition flow."""
    try:
        console.print("\n[bold]Add New Task[/bold]")

        title = Prompt.ask("Enter task title (1-100 chars)")
        if not (1 <= len(title) <= 100):
            console.print("[red]Title must be 1-100 characters[/red]")
            return

        description = Prompt.ask("Enter description (optional, max 500 chars)", default="")
        if len(description) > 500:
            console.print("[yellow]Description too long. Truncated to 500 chars.[/yellow]")
            description = description[:500]

        # Add task via service
        task = task_service.add_task(title=title, description=description)
        console.print(f"[green]✓ Task '{task.title}' added successfully![/green]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled[/yellow]")
    except Exception as e:
        console.print(f"[red]Error adding task: {str(e)}[/red]")
```

### Interactive List Tasks
```python
def interactive_list_tasks():
    """Interactive task listing with filtering options."""
    try:
        console.print("\n[bold]Filter Options:[/bold]")
        console.print("1. All tasks")
        console.print("2. Completed tasks only")
        console.print("3. Pending tasks only")

        filter_choice = Prompt.ask(
            "Select filter (1-3)",
            choices=["1", "2", "3"],
            default="1"
        )

        tasks = task_service.get_all_tasks()

        if filter_choice == "2":
            tasks = [t for t in tasks if t.completed]
        elif filter_choice == "3":
            tasks = [t for t in tasks if not t.completed]

        if not tasks:
            console.print("[yellow]No tasks found.[/yellow]")
            return

        display_tasks(tasks)  # Use table formatting from output formatting skill

    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled[/yellow]")
    except Exception as e:
        console.print(f"[red]Error listing tasks: {str(e)}[/red]")
```

### Interactive Update Task
```python
def interactive_update_task():
    """Interactive task update flow."""
    try:
        tasks = task_service.get_all_tasks()
        if not tasks:
            console.print("[yellow]No tasks available to update.[/yellow]")
            return

        display_tasks(tasks)

        task_id = int(Prompt.ask("Enter task ID to update"))

        # Find task
        task = next((t for t in tasks if t.id == task_id), None)
        if not task:
            console.print(f"[red]Task with ID {task_id} not found.[/red]")
            return

        console.print(f"\n[bold]Updating Task {task_id}:[/bold] {task.title}")

        new_title = Prompt.ask(f"Enter new title (current: {task.title})", default=task.title)
        new_description = Prompt.ask(
            f"Enter new description (current: {task.description or 'None'})",
            default=task.description or ""
        )

        if len(new_title) < 1 or len(new_title) > 100:
            console.print("[red]Title must be 1-100 characters[/red]")
            return

        if len(new_description) > 500:
            console.print("[yellow]Description too long. Truncated to 500 chars.[/yellow]")
            new_description = new_description[:500]

        updated_task = task_service.update_task(
            task_id=task_id,
            title=new_title,
            description=new_description,
            completed=task.completed
        )

        console.print(f"[green]✓ Task {updated_task.id} updated successfully![/green]")

    except ValueError:
        console.print("[red]Invalid task ID. Please enter a number.[/red]")
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled[/yellow]")
    except Exception as e:
        console.print(f"[red]Error updating task: {str(e)}[/red]")
```

### Interactive Delete Task
```python
def interactive_delete_task():
    """Interactive task deletion with confirmation."""
    try:
        tasks = task_service.get_all_tasks()
        if not tasks:
            console.print("[yellow]No tasks available to delete.[/yellow]")
            return

        display_tasks(tasks)

        task_id = int(Prompt.ask("Enter task ID to delete"))

        # Find task
        task = next((t for t in tasks if t.id == task_id), None)
        if not task:
            console.print(f"[red]Task with ID {task_id} not found.[/red]")
            return

        # Confirmation
        confirm = Prompt.ask(
            f"Are you sure you want to delete task '{task.title}'? (y/N)",
            choices=["y", "n"],
            default="n"
        )

        if confirm.lower() == "y":
            result = task_service.delete_task(task_id)
            if result:
                console.print(f"[green]✓ Task {task_id} deleted successfully![/green]")
            else:
                console.print(f"[red]Failed to delete task {task_id}.[/red]")
        else:
            console.print("[yellow]Deletion cancelled.[/yellow]")

    except ValueError:
        console.print("[red]Invalid task ID. Please enter a number.[/red]")
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled[/yellow]")
    except Exception as e:
        console.print(f"[red]Error deleting task: {str(e)}[/red]")
```

### Interactive Toggle Task
```python
def interactive_toggle_task():
    """Interactive task completion toggle."""
    try:
        tasks = task_service.get_all_tasks()
        if not tasks:
            console.print("[yellow]No tasks available to toggle.[/yellow]")
            return

        display_tasks(tasks)

        task_id = int(Prompt.ask("Enter task ID to toggle"))

        # Find task
        task = next((t for t in tasks if t.id == task_id), None)
        if not task:
            console.print(f"[red]Task with ID {task_id} not found.[/red]")
            return

        # Toggle completion status
        updated_task = task_service.toggle_task_completion(task_id)
        status = "completed" if updated_task.completed else "pending"

        console.print(f"[green]✓ Task {updated_task.id} marked as {status}![/green]")

    except ValueError:
        console.print("[red]Invalid task ID. Please enter a number.[/red]")
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled[/yellow]")
    except Exception as e:
        console.print(f"[red]Error toggling task: {str(e)}[/red]")
```

## Menu State Management

### Menu Navigation
```python
class MenuNavigator:
    """Handle menu navigation and state."""

    def __init__(self):
        self.current_menu = "main"
        self.previous_menus = []

    def navigate_to(self, menu_name: str):
        """Navigate to a different menu."""
        self.previous_menus.append(self.current_menu)
        self.current_menu = menu_name

    def go_back(self):
        """Go back to previous menu."""
        if self.previous_menus:
            self.current_menu = self.previous_menus.pop()

    def get_current_menu(self) -> str:
        """Get current menu name."""
        return self.current_menu
```

## Submenu Patterns

### Settings Menu
```python
def interactive_settings_menu():
    """Interactive settings menu."""
    while True:
        console.print("\n[bold]Settings[/bold]")
        console.print("1. View all settings")
        console.print("2. Change display options")
        console.print("3. Back to main menu")

        choice = Prompt.ask(
            "Select an option (1-3)",
            choices=["1", "2", "3"],
            default="3"
        )

        if choice == "1":
            console.print("[blue]Current settings displayed.[/blue]")
        elif choice == "2":
            console.print("[blue]Display options changed.[/blue]")
        elif choice == "3":
            break
```

## Error Handling in Interactive Menus

### Graceful Error Recovery
```python
def safe_menu_operation(operation, error_message):
    """Execute menu operation with error handling."""
    try:
        return operation()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        return None
    except Exception as e:
        console.print(f"[red]{error_message}: {str(e)}[/red]")
        return None
```

### Input Validation in Menus
```python
def get_valid_task_id() -> int:
    """Get a valid task ID with error handling."""
    while True:
        try:
            task_id = int(Prompt.ask("Enter task ID"))
            if task_id > 0:
                return task_id
            else:
                console.print("[red]Task ID must be positive.[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number.[/red]")
        except KeyboardInterrupt:
            console.print("\n[yellow]Operation cancelled.[/yellow]")
            return None
```

## Testing Interactive Menus

### Menu Flow Testing
```python
from unittest.mock import patch

def test_interactive_menu_flow():
    """Test interactive menu navigation flow."""
    inputs = iter(["1", "Test Task", "", "2", "3", "6"])

    with patch('rich.prompt.Prompt.ask', side_effect=lambda *args, **kwargs: next(inputs)):
        # Test menu flow without actually executing operations
        # This would need to mock the actual task service calls
        pass
```

### Menu Choice Validation Testing
```python
def test_menu_choice_validation(monkeypatch):
    """Test menu choice validation."""
    invalid_inputs = iter(["0", "7", "abc", "1"])
    valid_choice = "1"

    def mock_prompt(*args, **kwargs):
        try:
            val = next(invalid_inputs)
            if val not in ["1", "2", "3", "4", "5", "6"]:
                raise Exception("Invalid choice")
            return val
        except:
            return valid_choice

    monkeypatch.setattr('rich.prompt.Prompt.ask', mock_prompt)

    choice = get_menu_choice()
    assert choice == valid_choice
```

## Best Practices

### Menu Design Principles
- Provide clear navigation options
- Always include a way to exit or go back
- Validate user input consistently
- Handle keyboard interrupts gracefully
- Use consistent formatting throughout

### User Experience Guidelines
- Provide helpful prompts and instructions
- Confirm destructive actions (delete operations)
- Show current state and available options
- Handle errors without crashing the menu
- Keep menu response times fast and responsive