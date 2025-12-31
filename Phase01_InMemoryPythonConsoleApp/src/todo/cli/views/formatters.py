"""Task formatting functions for the Todo CLI application."""

from datetime import datetime, timedelta, time
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich.console import Group

from todo.models.task import Task, Priority, Recurrence
from todo.services.results import ReminderResult


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
    """Create a Rich table for displaying tasks with all Level 2 and 3 attributes."""
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
    table.add_column("Due Date", width=16, justify="center", style="magenta")
    table.add_column("Recurrence", width=12, justify="center", style="cyan")

    now = datetime.now()

    for task in tasks:
        # Status
        status_text = Text("[x]", style="bold green") if task.completed else Text("[ ]", style="bold red")

        # Priority
        pri_style = get_priority_style(task.priority)
        pri_text = Text(task.priority.name, style=pri_style)

        # Title with overdue styling
        title_text = Text(task.title)
        is_overdue = (task.due_date and
                      not task.completed and
                      task.due_date.time() != time(0, 0, 0) and  # Not date-only
                      task.due_date < now)
        if task.completed:
            title_text.stylize("strike dim")
        elif is_overdue:
            title_text.stylize("bold red")
        else:
            title_text.stylize("bold")

        # Description
        desc_text = truncate_text(task.description, 50) if task.description else "-"

        # Tags
        tags_text = ", ".join(sorted(task.tags)) if task.tags else "-"

        # Created Date
        created_text = task.created_at.strftime("%Y-%m-%d")

        # Due Date with overdue indicator
        if task.due_date:
            due_text = format_due_date(task.due_date)
            if is_overdue:
                due_text = f"{due_text} ⚠"
        else:
            due_text = "-"

        # Recurrence
        recur_text = format_recurrence(task.recurrence)

        table.add_row(
            str(task.id),
            status_text,
            pri_text,
            title_text,
            desc_text,
            tags_text,
            created_text,
            due_text,
            recur_text
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


def format_due_date(due_date: datetime) -> str:
    """Format due date for display, showing time only if not midnight."""
    if due_date is None:
        return "-"

    if due_date.time() == time(0, 0, 0):
        # Date-only task (midnight)
        return due_date.strftime("%Y-%m-%d")
    else:
        return due_date.strftime("%Y-%m-%d %I:%M %p")


def humanize_time_diff(td: timedelta) -> str:
    """Convert timedelta to human-readable string.

    Examples:
    - 30 minutes -> "30 mins"
    - 2 hours 30 mins -> "2 hrs 30 mins"
    - 3 days -> "3 days"
    - -30 minutes -> "30 mins overdue"
    """
    total_seconds = int(td.total_seconds())

    if total_seconds < 0:
        # Negative - overdue
        abs_seconds = abs(total_seconds)
        if abs_seconds < 60:
            return f"{abs_seconds} secs overdue"
        elif abs_seconds < 3600:
            mins = abs_seconds // 60
            return f"{mins} min{'s' if mins > 1 else ''} overdue"
        elif abs_seconds < 86400:
            hours = abs_seconds // 3600
            mins = (abs_seconds % 3600) // 60
            return f"{hours} hr{'s' if hours > 1 else ''} {mins} min{'s' if mins > 1 else ''} overdue"
        else:
            days = abs_seconds // 86400
            return f"{days} day{'s' if days > 1 else ''} overdue"
    else:
        # Positive - due in future
        if total_seconds < 60:
            return f"{total_seconds} secs"
        elif total_seconds < 3600:
            mins = total_seconds // 60
            return f"{mins} min{'s' if mins > 1 else ''}"
        elif total_seconds < 86400:
            hours = total_seconds // 3600
            mins = (total_seconds % 3600) // 60
            return f"{hours} hr{'s' if hours > 1 else ''} {mins} min{'s' if mins > 1 else ''}"
        else:
            days = total_seconds // 86400
            return f"{days} day{'s' if days > 1 else ''}"


def display_reminders(result: ReminderResult) -> None:
    """Display reminder panel with overdue and due-soon tasks."""
    if result.overdue_count == 0 and result.due_soon_count == 0:
        return  # Silent if no reminders

    console = Console()
    content = Text()

    if result.overdue_count > 0:
        content.append(f"[!] {result.overdue_count} overdue task(s)\n", style="bold red")
        for task in result.overdue_tasks[:5]:  # Show max 5
            time_diff = humanize_time_diff(datetime.now() - task.due_date)
            content.append(f"  - {task.title} ({time_diff})\n", style="red")

    if result.due_soon_count > 0:
        content.append(f"[o] {result.due_soon_count} due soon\n", style="bold yellow")
        for task in result.due_soon_tasks[:5]:  # Show max 5
            time_diff = humanize_time_diff(task.due_date - datetime.now())
            content.append(f"  - {task.title} (due in {time_diff})\n", style="yellow")

    console.print(Panel(content, title="[bold]Reminders[/bold]", border_style="cyan"))


def format_recurrence(recurrence: Recurrence) -> str:
    """Format recurrence pattern for display."""
    if recurrence == Recurrence.NONE:
        return "-"
    icons = {
        Recurrence.DAILY: "🔁 Daily",
        Recurrence.WEEKLY: "🔁 Weekly",
        Recurrence.MONTHLY: "🔁 Monthly",
    }
    return icons.get(recurrence, "-")
