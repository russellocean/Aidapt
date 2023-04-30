from agents.action_agent import ActionAgent
from agents.manager_agent import ManagerAgent
from database.codebase_database import convert_to_database
from ui.prompts import build_action_prompt, build_manager_prompt
from ui.user_interface import (
    choose_project_source,
    clone_repository,
    display_response_table,  # noqa: F401
    get_project_folder,
    get_user_input,
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
    codebase_database = convert_to_database(  # noqa: F841
        project_folder, project_source
    )  # noqa: F841

    # Step 3: Create Manager Agent and Action Agent with necessary tools
    manager_agent = ManagerAgent(codebase_database)
    action_agent = ActionAgent()

    # Step 4: Begin interaction loop between user and AI agent
    interaction_loop(manager_agent, action_agent)


def interaction_loop(
    manager_agent,
    action_agent,
):
    user_input = get_user_input()
    print(f"User input: {user_input}")

    task_results = [None]
    while True:
        manager_prompt = build_manager_prompt(
            user_input, previous_responses=task_results
        )
        task_list = manager_agent.process_input(manager_prompt)

        # display_task_list(task_list)

        # Check if the special value (None) is returned, and break the loop if it is
        if task_list is None:
            print("No more tasks to perform")
            # display_final_results()
            break

        for task in task_list:
            action_prompt = build_action_prompt(task)
            task_result = action_agent.process_input(action_prompt)
            # display_task_result(task_result)
            task_results.append(task_result)

            # Send the results back to the Manager Agent for evaluation
            manager_prompt = build_manager_prompt(
                user_input, previous_responses=task_results
            )
            task_list = manager_agent.process_input(manager_prompt)

        print(f"Task results: {task_results}")


if __name__ == "__main__":
    main()
