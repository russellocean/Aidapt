from ai_agent.ai_agent import AI_Agent
from database.codebase_database import convert_to_database
from ui.user_interface import (
    choose_project_source,
    clone_repository,
    display_response_table,
    get_project_folder,
    get_user_input,
    user_wants_to_exit,
)


def main():
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

    # Step 3: Create AI agent with necessary tools
    ai_agent = AI_Agent(codebase_database)

    # Step 4: Begin interaction loop between user and AI agent
    interaction_loop(ai_agent)


def interaction_loop(ai_agent):
    while True:
        # Get user input (e.g., text command or button press)
        user_input = get_user_input()
        print(f"User input: {user_input}")

        # Check if the user wants to exit the interaction loop
        if user_wants_to_exit(user_input):
            break

        # Process the user input and perform the requested action using the AI agent
        ai_response = ai_agent.process_input(user_input)

        # Display the AI response to the user
        # display_response(ai_response)
        display_response_table(ai_response)


if __name__ == "__main__":
    main()
