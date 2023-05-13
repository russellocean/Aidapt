import os

import git
import rich
from rich.console import Console
from rich.table import Table

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


def display_intermediate_response(output_type, feedback=None):
    if output_type == "response":
        # Display AI response
        display_agent_response(feedback)
    elif output_type == "tasks":
        # Display current tasks
        display_tasks(feedback)
    elif output_type == "prompt":
        # Display current prompt
        display_agent_prompt(feedback)
    elif output_type == "continuation":
        # Ask the user if they want to continue
        display_prompt(
            prompt_text="Do you want to continue? (yes/no):", style="bold green"
        )
        return receive_choice(choices=["yes", "no"])
    elif output_type == "info":
        # Display an informational message
        feedback = f"Info: {feedback}"
        display_prompt(prompt_text=feedback, style="bold blue")
    elif output_type == "warning":
        # Display a warning message
        feedback = f"Warning: {feedback}"
        display_prompt(prompt_text=feedback, style="bold yellow")
    elif output_type == "error":
        # Display an error message
        feedback = f"Error: {feedback}"
        display_prompt(prompt_text=feedback, style="bold red")
    elif output_type == "final_answer":
        # Display the final answer
        display_final_answer(feedback)
    elif output_type == "delegating":
        # Display a delegating message
        display_delegation_message(feedback)
    elif output_type == "tool":
        # Display a tool message
        display_tool_message(feedback)
    elif output_type == "memory":
        # Display a memory message
        display_memory_updates(feedback)
    else:
        display_prompt(prompt_text="Invalid output type given.", style="bold red")


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

    table = Table(
        show_header=True, header_style="bold green", box=rich.box.ROUNDED, pad_edge=True
    )
    table.add_column("Priority", justify="center", style="bold", no_wrap=True)
    table.add_column("Task", style="bold", no_wrap=True)
    table.add_column("Additional Info", style="none")

    for task in task_list:
        table.add_row(str(task["priority"]), task["task"], task["additional_info"])

    console.print(table)


def display_agent_response(feedback):
    console.print("\n[bold blue]Thoughts:[/bold blue]")
    console.print(feedback["thoughts"], style="blue")

    if feedback["criticisms"]:
        console.print("\n[bold red]Criticisms:[/bold red]")
        console.print(feedback["criticisms"], style="red")

    if "tools_to_run" in feedback:
        display_tools_to_run(feedback["tools_to_run"])

    if "agent_calls" in feedback:
        display_agent_calls(feedback["agent_calls"])

    # if "current_task_list" in feedback:
    #     display_current_task_list(feedback["current_task_list"])


def display_tools_to_run(tools):
    if tools:
        console.print("\n[bold green]Tools to run:[/bold green]")
        table = Table(
            show_header=True,
            header_style="bold green",
            box=rich.box.ROUNDED,
            pad_edge=True,
        )
        table.add_column("Tool", style="bold")
        table.add_column("Parameters")

        for tool in tools:
            parameters = ", ".join(str(param) for param in tool["parameters"])
            table.add_row(tool["tool"], parameters)

        console.print(table)


def display_agent_calls(agent_calls):
    if agent_calls:
        console.print("\n[bold green]Agent Calls:[/bold green]")
        table = Table(
            show_header=True,
            header_style="bold green",
            box=rich.box.ROUNDED,
            pad_edge=True,
        )
        table.add_column("Agent", style="bold underline")
        table.add_column("Task", style="bold underline")
        table.add_column("Message")

        for agent_call in agent_calls:
            table.add_row(
                str(agent_call["agent"]),
                str(agent_call["task"]),
                str(agent_call["message"]),
            )

        console.print(table)


def display_current_task_list(task_list):
    if task_list:
        console.print("\n[bold green]Current Task List:[/bold green]")
        table = Table(
            show_header=True,
            header_style="bold green",
            box=rich.box.ROUNDED,
            pad_edge=True,
        )
        table.add_column("Task ID", justify="center", style="bold", no_wrap=True)
        table.add_column("Task", style="bold", no_wrap=True)
        table.add_column("Completed", justify="center", style="bold", no_wrap=True)

        for task in task_list:
            completed = "✅" if task["completed"] else "❌"
            table.add_row(str(task["task_id"]), task["task"], completed)

        console.print(table)


def display_tasks(feedback):
    display_current_task_list(feedback)


def display_agent_prompt(feedback):
    console.print("\n[bold green]Agent Prompt:[/bold green]")
    table = Table(box=rich.box.ROUNDED, pad_edge=True)
    table.add_column("Prompt", style="bold cyan")
    table.add_row(feedback)
    console.print(table)


def display_final_answer(feedback):
    console.print("\n[bold green]Final Answer:[/bold green]")
    table = Table(box=rich.box.ROUNDED, pad_edge=True)
    table.add_column("Answer", style="bold magenta")
    table.add_row(feedback)
    console.print(table)


def display_delegation_message(feedback):
    console.print("\n[bold green]Delegation Message:[/bold green]")
    table = Table(box=rich.box.ROUNDED, pad_edge=True)
    table.add_column("Message", style="bold yellow")
    table.add_row(feedback)
    console.print(table)


def display_tool_message(feedback):
    console.print("\n[bold green]Tool Message:[/bold green]")
    table = Table(box=rich.box.ROUNDED, pad_edge=True)
    table.add_column("Message", style="bold blue")
    table.add_row(feedback)
    console.print(table)


def display_memory_updates(mem_updates):
    if mem_updates:
        console.print("\n[bold magenta]Memory Updates:[/bold magenta]")
        console.print(
            "Action: The type of action performed on the memory.\n"
            "Memory ID: The unique identifier of the memory.\n"
            "Content: The content of the memory.\n"
            "Metadata: Additional information related to the memory."
        )
        table = Table(
            show_header=True,
            header_style="bold magenta",
            box=rich.box.ROUNDED,
            pad_edge=True,
        )
        table.add_column("Action", style="bold")
        table.add_column("Memory ID")
        table.add_column("Content")
        table.add_column("Metadata")

        for update in mem_updates:
            memory_parameters = update.get("memory_parameters", {})
            memory_id = memory_parameters.get("id", "")
            content = memory_parameters.get("content", "")
            metadata = ", ".join(
                [f"{k}: {v}" for k, v in memory_parameters.get("metadata", {}).items()]
            )
            table.add_row(update.get("action", ""), str(memory_id), content, metadata)

        console.print(table)
