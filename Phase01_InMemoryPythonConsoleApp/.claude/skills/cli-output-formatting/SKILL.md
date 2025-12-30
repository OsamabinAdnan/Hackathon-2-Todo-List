# CLI Output Formatting Skill

This skill provides patterns and templates for implementing console output formatting using the Rich library in the CLI Todo application. Use this skill when implementing rich text formatting, tables, progress indicators, and other visual console output.

## When to Use This Skill

Use this skill when implementing:
- Task list display with Rich tables
- Formatted console output with colors and styles
- Progress indicators and loading states
- Error and success message formatting
- Interactive menu display with rich formatting

## Rich Table Formatting Patterns

### Basic Task Table
```python
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()

def display_tasks(tasks: List[Task]) -> None:
    """Display tasks in a formatted table."""
    if not tasks:
        console.print("[yellow]No tasks found.[/yellow]")
        return

    table = Table(title="Todo Tasks", box=box.SIMPLE)
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Title", style="magenta")
    table.add_column("Status", style="green")
    table.add_column("Description", style="dim")

    for task in tasks:
        status = "[green]✓[/green]" if task.completed else "[red]○[/red]"
        description = task.description if task.description else "[italic]No description[/italic]"

        # Truncate long descriptions
        if len(description) > 50:
            description = description[:47] + "..."

        table.add_row(
            str(task.id),
            task.title,
            status,
            description
        )

    console.print(table)
```

### Filtered Task Display
```python
def display_filtered_tasks(tasks: List[Task], filter_type: str = None) -> None:
    """Display tasks with optional filtering."""
    filtered_tasks = tasks
    if filter_type == "completed":
        filtered_tasks = [t for t in tasks if t.completed]
    elif filter_type == "pending":
        filtered_tasks = [t for t in tasks if not t.completed]

    if not filtered_tasks:
        console.print(f"[yellow]No {filter_type or 'tasks'} found.[/yellow]")
        return

    # Use the same table formatting as above
    display_tasks(filtered_tasks)
```

## Status and Summary Display

### Status Bar
```python
def display_status(tasks: List[Task]) -> None:
    """Display task summary status."""
    total = len(tasks)
    completed = sum(1 for task in tasks if task.completed)
    pending = total - completed

    status_text = f"[bold]Status:[/bold] {completed}/{total} completed ({pending} pending)"
    console.print(status_text)
```

### Task Summary
```python
def display_task_summary(task: Task) -> None:
    """Display detailed task information."""
    from rich.panel import Panel
    from rich.text import Text

    status = "Completed" if task.completed else "Pending"
    status_color = "green" if task.completed else "yellow"

    summary = Text()
    summary.append(f"ID: {task.id}\n", style="bold cyan")
    summary.append(f"Title: {task.title}\n", style="bold magenta")
    summary.append(f"Status: [{status_color}]{status}[/{status_color}]\n")
    if task.description:
        summary.append(f"Description: {task.description}")

    console.print(Panel(summary, title="Task Details", border_style="blue"))
```

## Progress and Loading Indicators

### Progress Display
```python
from rich.progress import Progress, SpinnerColumn, TextColumn

def show_loading_task_operation():
    """Show loading indicator during task operations."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(description="Processing...", total=None)
        # Perform task operation
        time.sleep(1)  # Simulate work
        progress.update(task, completed=True)
        console.print("[green]Operation completed![/green]")
```

## Color and Style Guidelines

### Consistent Color Scheme
```python
# Define consistent styles
TASK_COMPLETED_STYLE = "green"
TASK_PENDING_STYLE = "yellow"
TASK_TITLE_STYLE = "bold magenta"
TASK_ID_STYLE = "cyan"
ERROR_STYLE = "red"
SUCCESS_STYLE = "green"
WARNING_STYLE = "yellow"
INFO_STYLE = "blue"

def format_task_status(completed: bool) -> str:
    """Format task status with consistent colors."""
    status = "✓" if completed else "○"
    style = TASK_COMPLETED_STYLE if completed else TASK_PENDING_STYLE
    return f"[{style}]{status}[/{style}]"
```

## Interactive Menu Formatting

### Menu Display
```python
from rich.panel import Panel
from rich.columns import Columns

def display_main_menu() -> None:
    """Display the main menu with rich formatting."""
    menu_items = [
        "[bold blue]1.[/bold blue] Add Task",
        "[bold blue]2.[/bold blue] List Tasks",
        "[bold blue]3.[/bold blue] Update Task",
        "[bold blue]4.[/bold blue] Delete Task",
        "[bold blue]5.[/bold blue] Toggle Task",
        "[bold blue]6.[/bold blue] Quit"
    ]

    panel = Panel(
        "\n".join(menu_items),
        title="[bold green]Todo App Menu[/bold green]",
        border_style="bright_blue"
    )
    console.print(panel)
```

### Welcome Screen
```python
def display_welcome() -> None:
    """Display welcome message."""
    from rich.align import Align
    from rich.text import Text

    welcome_text = Text("Welcome to Todo CLI App", style="bold blue")
    welcome_text.highlight_words(["Todo CLI App"], "bold yellow")

    console.print(Align.center(welcome_text))
    console.print("\nManage your tasks efficiently from the command line!\n")
```

## Message Formatting

### Success Messages
```python
def display_success(message: str) -> None:
    """Display success message with formatting."""
    console.print(f"[bold green]✓ {message}[/bold green]")

def display_error(message: str) -> None:
    """Display error message with formatting."""
    console.print(f"[bold red]✗ {message}[/bold red]")

def display_warning(message: str) -> None:
    """Display warning message with formatting."""
    console.print(f"[bold yellow]⚠ {message}[/bold yellow]")
```

### Confirmation Messages
```python
def display_confirmation(message: str) -> None:
    """Display confirmation message with formatting."""
    console.print(f"[bold blue]? {message}[/bold blue]")
```

## Responsive Formatting

### Adaptive Table Width
```python
def display_responsive_tasks(tasks: List[Task]) -> None:
    """Display tasks with responsive table width."""
    width = console.size.width
    title_width = int(width * 0.4)  # 40% of console width for title

    table = Table(title="Tasks", box=box.SQUARE)
    table.add_column("ID", style="cyan", width=4)
    table.add_column("Title", style="magenta", width=title_width)
    table.add_column("Status", style="green", width=8)

    for task in tasks:
        status = "✓" if task.completed else "○"
        table.add_row(str(task.id), task.title, status)

    console.print(table)
```

## Testing Output Formatting

### Test Rich Output
```python
from rich.text import Text
from io import StringIO

def test_task_table_output():
    """Test task table output formatting."""
    from rich.console import Console

    # Capture output
    output = StringIO()
    console = Console(file=output, force_terminal=True)

    # Test with sample tasks
    tasks = [
        Task(id=1, title="Test Task", description="Test Description", completed=False)
    ]

    # Display tasks
    display_tasks(tasks)

    # Verify output contains expected elements
    output_content = output.getvalue()
    assert "Test Task" in output_content
    assert "1" in output_content
```

## Best Practices

### Formatting Principles
- Use consistent color scheme throughout the application
- Maintain readable contrast between text and background
- Use appropriate box styles for different contexts
- Keep tables responsive to terminal width
- Use emojis sparingly and appropriately

### Accessibility Considerations
- Ensure sufficient color contrast
- Use text indicators in addition to color
- Provide plain text alternatives when needed
- Avoid flashing or rapidly changing elements
- Test with different terminal themes