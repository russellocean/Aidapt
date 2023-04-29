import os

import git
import rich
from rich.console import Console
from rich.table import Table
from rich.text import Text

console = Console()


def display_prompt(prompt_text):
    # Display the prompt text to the user
    console.print(prompt_text, style="bold yellow")


def receive_choice(choices):
    # Get the user's choice from the given list of choices
    # Return the user's choice as a string
    user_choice = ""
    while user_choice not in choices:
        user_choice = input("Enter your choice: ").lower()
    return user_choice


def choose_project_source():
    # Prompt the user to choose between a folder, a repository, or none
    # Return the user's choice as a string ("folder", "repository", or "none")
    display_prompt("Enter the project source (folder/repository/none):")
    while True:
        project_source = input().lower()

        if project_source in ["folder", "repository", "none"]:
            return project_source
        else:
            console.print(
                "Invalid project source. Please enter folder, repository, or none.",
                style="bold red",
            )


def get_project_folder():
    # Prompt the user to select a project folder on their computer
    # Return the selected folder path as a string
    display_prompt("Enter the path to the project folder:")
    folder_path = input()
    return folder_path


def clone_repository():
    # Prompt the user to input the repository URL
    # Clone the repository to a local folder and return the folder path
    display_prompt("Enter the repository URL:")
    repo_url = receive_repository_url()
    folder_path = clone_repo_to_local_folder(repo_url)
    return folder_path


def receive_repository_url():
    # Get the repository URL from the user
    # Return the URL as a string
    repo_url = input("Enter the repository URL: ")
    return repo_url


def clone_repo_to_local_folder(repo_url):
    # Clone the given repository URL to a local folder
    # Return the local folder path
    folder_name = os.path.basename(repo_url)
    local_path = os.path.join(os.getcwd(), folder_name)
    git.Repo.clone_from(repo_url, local_path)
    return local_path


def get_user_input():
    # Get the user input (e.g., text command or button press)
    # Return the user input as a string
    display_prompt("Enter your objective:")
    user_input = input()
    return user_input


def display_response(ai_response):
    # Display the AI response to the user
    console.print("\n[bold green]Commands and Parameters:[/bold green]")
    console.print(ai_response["commands_and_parameters"], style="green")

    console.print("\n[bold blue]Thoughts:[/bold blue]")
    console.print(ai_response["thoughts"], style="blue")

    if ai_response["criticisms"] != "None":
        console.print("\n[bold red]Criticisms:[/bold red]")
        console.print(ai_response["criticisms"], style="red")

    console.print("\n[bold magenta]Additional Info:[/bold magenta]")
    console.print(ai_response["additional_info"], style="magenta")


def display_response_table(ai_response):
    table = Table(show_header=False, box=rich.box.ROUNDED, pad_edge=True)

    table.add_column("Category", justify="left", style="bold", no_wrap=True)
    table.add_column("Description", style="none")

    command = ai_response["commands_and_parameters"]["command"]
    parameters = ai_response["commands_and_parameters"]["parameters"]
    formatted_parameters = "\n".join(
        [f"{key}: {value}" for key, value in parameters.items()]
    )

    table.add_row(Text("Command:", style="bold cyan"), Text(command, style="cyan"))
    if formatted_parameters:
        table.add_row(
            Text("Parameters:", style="bold cyan"),
            Text(formatted_parameters, style="cyan"),
        )

    table.add_row(Text("Thoughts:", style="bold blue"), ai_response["thoughts"])

    if ai_response["criticisms"] != "None":
        table.add_row(Text("Criticisms:", style="bold red"), ai_response["criticisms"])

    table.add_row(
        Text("Additional Info:", style="bold magenta"), ai_response["additional_info"]
    )

    console.print(table)


def user_wants_to_exit(user_input):
    # Check if the user wants to exit the interaction loop
    # Return a boolean value
    return user_input.strip().lower() == "exit"
