"""Task formatting functions for the Todo CLI application."""


from rich.console import Console
from rich.table import Table
from rich.text import Text

from todo.models.task import Task


def format_task_status(task: Task) -> str:
    """Format the completion status of a task.

    Args:
        task: The task to format.

    Returns:
        Formatted status string with symbol.
    """
    if task.completed:
        return "[green]✓[/green]"
    return "[yellow]○[/yellow]"


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text to a maximum length with ellipsis.

    Args:
        text: The text to truncate.
        max_length: Maximum length before truncation (default: 50).

    Returns:
        Truncated text with "..." appended if needed.
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def format_task_for_list(task: Task, include_description: bool = True) -> Text:
    """Format a single task for display in a list.

    Args:
        task: The task to format.
        include_description: Whether to include description (default: True).

    Returns:
        Rich Text object with formatted task.
    """
    text = Text()

    # Status symbol and Task ID
    if task.completed:
        text.append("[x] ", style="bold green")
    else:
        text.append("[ ] ", style="bold yellow")

    text.append(f"[{task.id}] ", style="dim")

    # Title with styling for completed tasks
    if task.completed:
        text.append(task.title, style="strike dim")
    else:
        text.append(task.title, style="bold")

    # Description (truncated)
    if include_description and task.description:
        text.append("\n")
        text.append(
            f"   Description: {truncate_text(task.description, 50)}",
            style="dim italic",
        )

    return text


def format_task_table(tasks: list[Task]) -> Table:
    """Create a Rich table for displaying tasks matching properCLI2.png layout.

    Args:
        tasks: List of tasks to display.

    Returns:
        Rich Table with task data.
    """
    table = Table(
        show_header=True,
        header_style="bold white",
        box=None,
        show_edge=False,
        show_lines=False,
        expand=True,
        padding=(0, 1)
    )

    table.add_column("ID", width=4, justify="right", style="cyan")
    table.add_column("St", width=4, justify="center")
    table.add_column("Title", ratio=2, style="white")
    table.add_column("Description", ratio=3, style="dim")

    for task in tasks:
        # Match colors from screenshot
        status = "[x]" if task.completed else "[ ]"
        status_style = "bold green" if task.completed else "bold red"

        # Strikethrough for completed tasks
        title_text = Text(task.title)
        if task.completed:
            title_text.stylize("strike dim")
        else:
            title_text.stylize("bold")

        table.add_row(
            str(task.id),
            Text(status, style=status_style),
            title_text,
            Text(truncate_text(task.description, 50), style="dim"),
        )

    return table


def format_task_list(
    tasks: list[Task],
    console: Console,
) -> None:
    """Display a formatted list of tasks wrapped in a panel.

    Args:
        tasks: List of tasks to display.
        console: Rich Console instance for output.
    """
    from rich.panel import Panel
    from rich.console import Group

    if not tasks:
        console.print(Panel("[yellow]No tasks yet. Run 'add' command to add one.[/yellow]", title="Tasks", border_style="blue"))
        return

    completed_count = sum(1 for t in tasks if t.completed)

    table = format_task_table(tasks)

    footer = Text.from_markup(f"\n[bold]{completed_count}/{len(tasks)} completed[/bold]")

    group = Group(table, footer)

    panel = Panel(
        group,
        title="[bold white]Task List[/bold white]",
        border_style="blue",
        padding=(1, 2)
    )

    console.print(panel)


def format_empty_state() -> str:
    """Format the empty state message.

    Returns:
        Formatted empty state message.
    """
    return "[yellow]No tasks yet. Run 'add' command to add one.[/yellow]"


def format_task_count(completed: int, total: int) -> str:
    """Format the task count summary.

    Args:
        completed: Number of completed tasks.
        total: Total number of tasks.

    Returns:
        Formatted count string.
    """
    return f"[bold]{completed}/{total} completed[/bold]"


def format_success_message(action: str, task_id: int) -> str:
    """Format a success message for a task action.

    Args:
        action: The action performed (e.g., "added", "updated", "deleted").
        task_id: The ID of the task.

    Returns:
        Formatted success message.
    """
    return f"[green]Task {task_id} {action}[/green]"


def format_error_message(error: str) -> str:
    """Format an error message.

    Args:
        error: The error message.

    Returns:
        Formatted error message.
    """
    return f"[red]Error: {error}[/red]"


def format_validation_error(field: str, message: str) -> str:
    """Format a validation error message.

    Args:
        field: The field that failed validation.
        message: The validation error message.

    Returns:
        Formatted validation error.
    """
    return f"[red]{field}: {message}[/red]"
