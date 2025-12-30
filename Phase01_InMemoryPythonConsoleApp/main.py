"""Main CLI application for the Todo application using Typer and Rich."""

from typing import Optional

import typer
from rich.console import Console
from rich.theme import Theme

from todo.services.task_service import TaskService, get_task_service

# Create Typer app
app = typer.Typer(
    name="todo",
    help="A simple Todo CLI application",
    add_completion=False,
)

# Create Rich console with custom theme
console = Console()


def get_service() -> TaskService:
    """Get the task service instance."""
    return get_task_service()


@app.command("list", help="List all tasks")
def list_tasks() -> None:
    """Display all tasks."""
    service = get_service()
    tasks = service.get_all_tasks()

    if not tasks:
        console.print("[yellow]No tasks yet. Run 'todo add' to add one.[/yellow]")
        return

    console.print(f"[bold]Tasks ({len(tasks)} total)[/bold]")
    for task in tasks:
        status = "[green]✓[/green]" if task.completed else "[yellow]○[/yellow]"
        console.print(f"{status} [{task.id}] {task.title}")


@app.command("add", help="Add a new task")
def add_task(
    title: str = typer.Argument(..., help="Task title (1-100 characters)"),
    description: str = typer.Option("", "--description", "-d", help="Task description (0-500 characters)"),
) -> None:
    """Add a new task."""
    service = get_service()
    try:
        task = service.add_task(title, description)
        console.print(f"[green]Task added: {task.id} - {task.title}[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


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
    title: Optional[str] = typer.Option(None, "--title", "-t", help="New title (1-100 characters)"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="New description (0-500 characters)"),
) -> None:
    """Update a task's title and/or description."""
    service = get_service()
    try:
        task = service.update_task(task_id, title=title, description=description)
        console.print(f"[green]Task {task_id} updated[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@app.command("toggle", help="Toggle task completion")
def toggle_task(
    task_id: int = typer.Argument(..., help="Task ID to toggle"),
) -> None:
    """Toggle a task's completion status."""
    service = get_service()
    try:
        task = service.toggle_task_completion(task_id)
        status = "complete" if task.completed else "incomplete"
        console.print(f"[green]Task {task_id} marked {status}[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@app.command("complete", help="Mark task as complete")
def mark_complete(
    task_id: int = typer.Argument(..., help="Task ID to mark complete"),
) -> None:
    """Mark a task as complete."""
    service = get_service()
    try:
        task = service.mark_task_complete(task_id)
        console.print(f"[green]Task {task_id} marked complete[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@app.command("incomplete", help="Mark task as incomplete")
def mark_incomplete(
    task_id: int = typer.Argument(..., help="Task ID to mark incomplete"),
) -> None:
    """Mark a task as incomplete."""
    service = get_service()
    try:
        task = service.mark_task_incomplete(task_id)
        console.print(f"[green]Task {task_id} marked incomplete[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@app.command("menu", help="Run interactive menu")
def interactive_menu() -> None:
    """Run the interactive menu system."""
    from todo.cli.views.menu import run_menu

    run_menu()


@app.callback(invoke_without_command=True)
def main_callback(ctx: typer.Context) -> None:
    """Default callback to run menu if no command is provided."""
    if ctx.invoked_subcommand is None:
        interactive_menu()


def main() -> None:
    """Main entry point for the CLI application."""
    app()


if __name__ == "__main__":
    main()
