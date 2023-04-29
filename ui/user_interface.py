import os

import git


def display_prompt(prompt_text):
    # Display the prompt text to the user
    print(prompt_text)
    # Eventually use a UI frameworks


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
    while True:
        project_source = input(
            "Enter the project source (folder/repository/none): "
        ).lower()

        if project_source in ["folder", "repository", "none"]:
            return project_source
        else:
            print("Invalid project source. Please enter folder, repository, or none.")


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
    user_input = input("Enter your objective: ")
    return user_input


def display_response(ai_response):
    # Display the AI response to the user
    # Takes the AI response as input
    print(ai_response)


def user_wants_to_exit(user_input):
    # Check if the user wants to exit the interaction loop
    # Return a boolean value
    return user_input.strip().lower() == "exit"
