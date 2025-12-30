"""Interactive menu system for the Todo CLI application."""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from todo.services.task_service import TaskService, get_task_service

console = Console()


def display_menu() -> None:
    """Display the main menu options."""
    menu_text = Text()
    menu_text.append("Todo - Manage your tasks\n\n", style="bold yellow")
    menu_text.append("1. ", style="bold")
    menu_text.append("Add Task - Create new task with title and optional description\n")
    menu_text.append("2. ", style="bold")
    menu_text.append("List Tasks - Display all tasks with status\n")
    menu_text.append("3. ", style="bold")
    menu_text.append("Update Task - Edit existing task details\n")
    menu_text.append("4. ", style="bold")
    menu_text.append("Delete Task - Remove task (with confirmation)\n")
    menu_text.append("5. ", style="bold")
    menu_text.append("Toggle - Mark task complete or incomplete\n")
    menu_text.append("6. ", style="bold")
    menu_text.append("Quit - Exit application\n")

    panel = Panel(
        menu_text,
        title="[bold]Todo Application[/bold]",
        border_style="blue",
    )
    console.print(panel)


def get_menu_choice() -> int:
    """Get and validate menu choice from user.

    Returns:
        The validated menu choice (1-6).

    Raises:
        ValueError: If input is not a valid integer in range.
    """
    while True:
        try:
            choice = Prompt.ask(
                "[bold cyan]Enter option (1-6)[/bold cyan]"
            )
            choice_int = int(choice)
            if 1 <= choice_int <= 6:
                return choice_int
            else:
                console.print(
                    "[red]Invalid option. Please enter 1-6.[/red]"
                )
        except ValueError:
            console.print("[red]Please enter a valid number (1-6).[/red]")


def handle_add_task(service: TaskService) -> None:
    """Handle the Add Task menu option."""
    console.print("\n[bold]Add New Task[/bold]")
    title = Prompt.ask("[bold]Enter task title (1-100 chars):[/bold]").strip()
    if not title:
        console.print("[red]Title cannot be empty.[/red]")
        return

    if len(title) > 100:
        console.print("[red]Title cannot exceed 100 characters.[/red]")
        return

    description = Prompt.ask(
        "[bold]Enter description (optional, 0-500 chars):[/bold]"
    ).strip()

    if len(description) > 500:
        console.print("[red]Description cannot exceed 500 characters.[/red]")
        return

    try:
        task = service.add_task(title, description)
        console.print(f"[green]Task added successfully! ID: {task.id}[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def handle_list_tasks(service: TaskService) -> None:
    """Handle the List Tasks menu option."""
    from todo.cli.views.formatters import format_task_list

    tasks = service.get_all_tasks()
    format_task_list(tasks, console)


def handle_update_task(service: TaskService) -> None:
    """Handle the Update Task menu option."""
    console.print("\n[bold]Update Task[/bold]")

    try:
        task_id = int(
            Prompt.ask("[bold]Enter task ID to update:[/bold]").strip()
        )
    except ValueError:
        console.print("[red]Invalid task ID.[/red]")
        return

    try:
        task = service.get_task(task_id)
        console.print(f"[yellow]Current: {task.title}[/yellow]")
        if task.description:
            console.print(f"[dim]Description: {task.description}[/dim]")

        new_title_raw = Prompt.ask(
            "[bold]Enter new title (press Enter to keep current):[/bold]",
            default="",
        ).strip()

        new_description_raw = Prompt.ask(
            "[bold]Enter new description (press Enter to keep current):[/bold]",
            default="",
        ).strip()

        new_title: str | None = new_title_raw if new_title_raw else None
        new_description: str | None = new_description_raw if new_description_raw else None

        _ = service.update_task(
            task_id, title=new_title, description=new_description
        )
        console.print(
            f"[green]Task {task_id} updated successfully![/green]"
        )
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def handle_delete_task(service: TaskService) -> None:
    """Handle the Delete Task menu option."""
    console.print("\n[bold]Delete Task[/bold]")

    try:
        task_id = int(
            Prompt.ask("[bold]Enter task ID to delete:[/bold]").strip()
        )
    except ValueError:
        console.print("[red]Invalid task ID.[/red]")
        return

    try:
        task = service.get_task(task_id)
        console.print(f"[yellow]Task: {task.title}[/yellow]")

        confirm = Prompt.ask(
            "[bold red]Delete this task? This cannot be undone. (y/n):[/bold red]",
            default="n",
        ).strip().lower()

        if confirm == "y":
            service.delete_task(task_id)
            console.print(f"[green]Task {task_id} deleted.[/green]")
        else:
            console.print("[dim]Deletion cancelled.[/dim]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def handle_toggle_task(service: TaskService) -> None:
    """Handle the Toggle menu option - mark task complete or incomplete."""
    console.print("\n[bold]Toggle Task Completion[/bold]")

    try:
        task_id = int(
            Prompt.ask("[bold]Enter task ID:[/bold]").strip()
        )
    except ValueError:
        console.print("[red]Invalid task ID.[/red]")
        return

    try:
        task = service.toggle_task_completion(task_id)
        status = "complete" if task.completed else "incomplete"
        console.print(
            f"[green]Task {task_id} is now {status}.[/green]"
        )
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def run_menu() -> None:
    """Run the interactive menu system."""
    service = get_task_service()

    while True:
        display_menu()
        choice = get_menu_choice()

        if choice == 1:
            handle_add_task(service)
        elif choice == 2:
            handle_list_tasks(service)
        elif choice == 3:
            handle_update_task(service)
        elif choice == 4:
            handle_delete_task(service)
        elif choice == 5:
            handle_toggle_task(service)
        elif choice == 6:
            console.print("\n[bold cyan]Goodbye![/bold cyan]")
            break

        console.print("")  # Add spacing
