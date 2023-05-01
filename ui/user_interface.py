import os

import git
import rich
from rich.console import Console
from rich.table import Table
from rich.text import Text

console = Console()


def display_prompt(prompt_text, style="bold yellow"):
    console.print(prompt_text, style=style)


def receive_choice(choices):
    user_choice = ""
    while user_choice not in choices:
        user_choice = input("Enter your choice: ").lower()
    return user_choice


def separator():
    console.rule(style="dim")


def choose_project_source():
    display_prompt("Enter the project source (folder/repository/none):")
    while True:
        project_source = input().lower()

        if project_source in ["folder", "repository", "none"]:
            return project_source
        else:
            display_prompt(
                "Invalid project source. Please enter folder, repository, or none.",
                style="bold red",
            )


def get_project_folder():
    display_prompt("Enter the path to the project folder:")
    folder_path = input()
    return folder_path


def clone_repository():
    display_prompt("Enter the repository URL:")
    repo_url = receive_repository_url()
    folder_path = clone_repo_to_local_folder(repo_url)
    return folder_path


def receive_repository_url():
    repo_url = input("Enter the repository URL: ")
    return repo_url


def clone_repo_to_local_folder(repo_url):
    folder_name = os.path.basename(repo_url)
    local_path = os.path.join(os.getcwd(), folder_name)
    git.Repo.clone_from(repo_url, local_path)
    return local_path


def get_user_input():
    display_prompt("Enter your objective:")
    user_input = input()
    return user_input


def display_user_input(user_input):
    console.print("\n[bold yellow]User Input:[/bold yellow]")
    console.print(user_input, style="yellow")


def display_manager_task_list(task_list):
    console.print("\n[bold green]Manager Task List:[/bold green]")
    console.print(task_list, style="green")


def display_task_results(task_list, task_results):
    formatted_results = []

    min_length = min(len(task_list), len(task_results))

    for index in range(min_length):
        task_result = task_results[index]
        if task_result is None:
            continue

        task = task_list[index]
        display_task_result(task, task_result)

    console.print("\n".join(formatted_results), style="magenta")


def display_task_result(task, task_results):
    for task_result in task_results:
        table = Table(show_header=False, box=rich.box.ROUNDED, pad_edge=True)
        table.add_column("Category", justify="left", style="bold", no_wrap=True)
        table.add_column("Description", style="none")

        task_str = f"Task: {task['task']} ({task['additional_info']})"
        thoughts_str = task_result["thoughts"]
        tool_str = f"Tool Used: {task_result['command']}"
        result_str = f"Tool Result: {task_result['result']}"

        table.add_row(
            Text("Task:", style="bold magenta"), Text(task_str, style="magenta")
        )
        table.add_row(
            Text("Thoughts:", style="bold blue"), Text(thoughts_str, style="blue")
        )
        table.add_row(Text("Tool:", style="bold cyan"), Text(tool_str, style="cyan"))
        table.add_row(
            Text("Result:", style="bold green"), Text(result_str, style="green")
        )

        console.print(table)
