"""Task formatting functions for the Todo CLI application."""

from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich.console import Group

from todo.models.task import Task, Priority


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def get_priority_style(priority: Priority) -> str:
    """Get Rich color style for priority levels."""
    if priority == Priority.HIGH:
        return "bold red"
    if priority == Priority.MEDIUM:
        return "bold yellow"
    if priority == Priority.LOW:
        return "bold green"
    return "dim white"


def format_task_table(tasks: list[Task]) -> Table:
    """Create a Rich table for displaying tasks with all Level 2 attributes."""
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
    table.add_column("Pri", width=6, justify="center")
    table.add_column("Title", ratio=2, style="white")
    table.add_column("Description", ratio=2, style="dim italic")
    table.add_column("Tags", ratio=1, style="blue")
    table.add_column("Created", width=12, justify="center", style="dim cyan")
    table.add_column("Due Date", width=12, justify="center", style="magenta")

    for task in tasks:
        # Status
        status_text = Text("[x]", style="bold green") if task.completed else Text("[ ]", style="bold red")

        # Priority
        pri_style = get_priority_style(task.priority)
        pri_text = Text(task.priority.name, style=pri_style)

        # Title
        title_text = Text(task.title)
        if task.completed:
            title_text.stylize("strike dim")
        else:
            title_text.stylize("bold")

        # Description
        desc_text = truncate_text(task.description, 50) if task.description else "-"

        # Tags
        tags_text = ", ".join(sorted(task.tags)) if task.tags else "-"

        # Created Date
        created_text = task.created_at.strftime("%Y-%m-%d")

        # Due Date
        due_text = task.due_date.isoformat() if task.due_date else "-"

        table.add_row(
            str(task.id),
            status_text,
            pri_text,
            title_text,
            desc_text,
            tags_text,
            created_text,
            due_text
        )

    return table


def format_task_list(
    tasks: list[Task],
    console: Console,
    title: str = "Task List"
) -> None:
    """Display a formatted list of tasks wrapped in a panel."""
    if not tasks:
        console.print(Panel("[yellow]No tasks found matching criteria. Run 'add' to add one.[/yellow]", title=title, border_style="blue"))
        return

    completed_count = sum(1 for t in tasks if t.completed)
    table = format_task_table(tasks)
    footer = Text.from_markup(f"\n[bold]{completed_count}/{len(tasks)} tasks shown[/bold]")

    group = Group(table, footer)
    panel = Panel(
        group,
        title=f"[bold white]{title}[/bold white]",
        border_style="blue",
        padding=(1, 2)
    )

    console.print(panel)
