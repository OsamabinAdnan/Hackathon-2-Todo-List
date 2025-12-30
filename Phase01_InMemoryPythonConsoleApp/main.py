"""Main CLI application for the Todo application using Typer and Rich."""

from typing import Optional, List
from datetime import date

import typer
from rich.console import Console

from todo.models.task import Priority
from todo.services.task_service import TaskService, get_task_service
from todo.cli.views.formatters import format_task_list

# Create Typer app
app = typer.Typer(
    name="todo",
    help="A powerful Todo CLI application",
    add_completion=False,
)

# Create Rich console
console = Console()


def get_service() -> TaskService:
    """Get the task service instance."""
    return get_task_service()


@app.command("list", help="List all tasks with filtering and sorting")
def list_tasks(
    status: Optional[str] = typer.Option(None, "--status", help="Filter by status (todo, done)"),
    priority: Optional[str] = typer.Option(None, "--priority", "-p", help="Filter by priority"),
    tag: Optional[List[str]] = typer.Option(None, "--tag", "-t", help="Filter by tags"),
    sort: Optional[str] = typer.Option(None, "--sort", "-s", help="Sort by (priority, date, title, due_date)"),
) -> None:
    """Display tasks with optional filters."""
    service = get_service()

    # Process filters
    is_completed = None
    if status:
        if status.lower() == "done":
            is_completed = True
        elif status.lower() == "todo":
            is_completed = False

    p_enum = Priority.from_str(priority) if priority else None
    tag_set = set(tag) if tag else None

    result = service.search_tasks(
        status=is_completed,
        priority=p_enum,
        tags=tag_set,
        sort_by=sort
    )

    format_task_list(result.tasks, console, title="Filtered Task List")


@app.command("add", help="Add a new task")
def add_task(
    title: str = typer.Argument(..., help="Task title (1-100 characters)"),
    description: str = typer.Option("", "--description", "-d", help="Task description (0-500 characters)"),
    priority: str = typer.Option("NONE", "--priority", "-p", help="Priority (HIGH, MEDIUM, LOW, NONE)"),
    tags: Optional[str] = typer.Option(None, "--tags", help="Comma-separated tags"),
    due_date: Optional[str] = typer.Option(None, "--due", help="Due date (YYYY-MM-DD)"),
) -> None:
    """Add a new task."""
    service = get_service()
    try:
        p_enum = Priority.from_str(priority)
        tag_set = {t.strip() for t in tags.split(",")} if tags else set()
        due = date.fromisoformat(due_date) if due_date else None

        task = service.add_task(
            title=title,
            description=description,
            priority=p_enum,
            tags=tag_set,
            due_date=due
        )
        console.print(f"[green]Task added: {task.id} - {task.title}[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@app.command("search", help="Search tasks by keyword")
def search_tasks(
    query: str = typer.Argument(..., help="Search keyword"),
    status: Optional[str] = typer.Option(None, "--status"),
    priority: Optional[str] = typer.Option(None, "--priority", "-p"),
) -> None:
    """Search tasks by title/description."""
    service = get_service()

    is_completed = None
    if status:
        is_completed = status.lower() == "done"

    p_enum = Priority.from_str(priority) if priority else None

    result = service.search_tasks(keyword=query, status=is_completed, priority=p_enum)
    format_task_list(result.tasks, console, title=f"Search Results: '{query}'")


@app.command("delete", help="Delete a task")
def delete_task(
    task_id: int = typer.Argument(..., help="Task ID to delete"),
) -> None:
    """Delete a task by ID."""
    service = get_service()
    try:
        service.delete_task(task_id)
        console.print(f"[green]Task {task_id} deleted[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@app.command("update", help="Update a task")
def update_task(
    task_id: int = typer.Argument(..., help="Task ID to update"),
    title: Optional[str] = typer.Option(None, "--title", "-t"),
    description: Optional[str] = typer.Option(None, "--description", "-d"),
    priority: Optional[str] = typer.Option(None, "--priority", "-p"),
    tags: Optional[str] = typer.Option(None, "--tags"),
    due_date: Optional[str] = typer.Option(None, "--due"),
) -> None:
    """Update task attributes."""
    service = get_service()
    try:
        p_enum = Priority.from_str(priority) if priority else None
        tag_set = {t.strip() for t in tags.split(",")} if tags else None
        due = date.fromisoformat(due_date) if due_date else None

        service.update_task(
            task_id,
            title=title,
            description=description,
            priority=p_enum,
            tags=tag_set,
            due_date=due
        )
        console.print(f"[green]Task {task_id} updated[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@app.command("toggle", help="Toggle task completion")
def toggle_task(
    task_id: int = typer.Argument(..., help="Task ID to toggle"),
) -> None:
    """Toggle status."""
    service = get_service()
    try:
        task = service.toggle_task_completion(task_id)
        status = "complete" if task.completed else "incomplete"
        console.print(f"[green]Task {task_id} marked {status}[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@app.command("menu", help="Run interactive menu")
def interactive_menu() -> None:
    """Run interactive menu system."""
    from todo.cli.views.menu import run_menu
    run_menu()


@app.callback(invoke_without_command=True)
def main_callback(ctx: typer.Context) -> None:
    """Default to menu."""
    if ctx.invoked_subcommand is None:
        interactive_menu()


def main() -> None:
    """Entry point."""
    app()


if __name__ == "__main__":
    main()
