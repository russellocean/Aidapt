from agents.agent import Agent
from agents.manager_agent import AgentManager
from database.codebase_database import convert_to_database
from database.memory_database import MemoryDatabase
from ui.user_interface import (
    choose_project_source,
    clone_repository,
    display_intermediate_response,
    display_user_input,
    get_project_folder,
    get_user_input,
)


def main():
    # Set the callback for the Agent class, dont set output raw steps to console.
    Agent.set_callback(display_intermediate_response)

    # Create the global memory database.
    memory_database = MemoryDatabase()
    memory_database.clear_all_memories()

    # Set the memory database for the Agent class.
    Agent.set_memory_database(memory_database)

    # Welcome the user to
    # Step 1: Initialize project
    project_source = choose_project_source()

    project_folder = None
    if project_source == "folder":
        project_folder = get_project_folder()
    elif project_source == "repository":
        project_folder = clone_repository()

    # Step 2: Convert project to AI-friendly database
    codebase_database = convert_to_database(project_folder, project_source)

    # Step 3: Create Manager Agent and Action Agent with necessary tools
    manager_agent = AgentManager()

    # Step 4: Begin interaction loop between user and AI agent
    interaction_loop(manager_agent, codebase_database)


def interaction_loop(manager_agent, codebase_database=None):
    while True:
        user_input = get_user_input()
        if user_input == "":
            user_input = "Write a Python program that prints 'Hello World!' in the directory /Users/russellocean/Dev/test"

        display_user_input(user_input)

        if user_input == "exit":
            break

        if user_input == "help":
            # display_help()
            continue

        manager_agent.run(
            users_objective=user_input,
            confirmation=True,
        )


if __name__ == "__main__":
    main()
