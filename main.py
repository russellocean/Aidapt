from agents.agent import Agent
from agents.manager_agent import AgentManager
from database.codebase_database import convert_to_database
from database.memory_database import MemoryDatabase
from ui.user_interface import (
    ask_restart_project_context,
    choose_project_source,
    clone_repository,
    display_intermediate_response,
    display_user_input,
    get_project_folder,
    get_user_input,
)


def main():
    # Step 1: Set the callback for the Agent class. This is necessary for processing and interacting with the agent responses.
    # Note: We are not outputting raw steps to the console.
    Agent.set_callback(display_intermediate_response)

    # Step 2: Create the global memory database. This will store the states and data that the AI agent needs to remember across interactions.
    memory_database = MemoryDatabase()

    # Step 3: Ask the user if they want to restart the project context. If yes, the memory database is cleared to start afresh.
    restart_project_context = ask_restart_project_context()
    if restart_project_context:
        # Clear the entire memory database, erasing any previous context or state.
        memory_database.clear_all_memories()

    # Step 4: Set the memory database for the Agent class. This lets the agent access and interact with the memory database we just created.
    Agent.set_memory_database(memory_database)

    # Step 5: Prompt the user to choose the source of the project. The project can be sourced from a local folder or a remote repository.
    project_source = choose_project_source()

    # Step 6: If the project is sourced from a folder, ask for the folder path.
    # If the project is sourced from a repository, clone the repository.
    project_folder = None
    if project_source == "folder":
        project_folder = get_project_folder()
    elif project_source == "repository":
        project_folder = clone_repository()

    # Step 7: Convert the sourced project into an AI-friendly database. This will help the AI understand and interact with the codebase effectively.
    codebase_database = convert_to_database(project_folder, project_source)

    # Step 8: Create an instance of the Manager Agent. This agent is responsible for managing the high-level operations and interactions.
    manager_agent = AgentManager()

    # Step 9: Begin the interaction loop between the user and the AI agent. This is where the bulk of the AI-user interaction happens.
    interaction_loop(manager_agent, codebase_database)


def interaction_loop(manager_agent, codebase_database=None):
    # This is an infinite loop that will continue to ask for and process user input until the user enters "exit".
    while True:
        # Step 1: Get the user input. This is what the user wants the AI to do.
        user_input = get_user_input()

        # If no input is provided by the user, set a default input for testing.
        if user_input == "":
            import os

            project_directory = os.path.dirname(os.path.abspath(__file__))
            project_directory = os.path.join(project_directory, "test")

            user_input = f"Write a Python program that prints 'Hello World!' in the directory {project_directory}"

        display_user_input(user_input)

        if user_input == "exit":
            break

        if user_input == "help":
            # display_help()
            continue

        # Run the manager agent with the user's objective. The 'confirmation' parameter set to True means the agent will confirm actions before taking them.
        manager_agent.run(
            users_objective=user_input,
            confirmation=True,
        )


if __name__ == "__main__":
    main()
