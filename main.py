from agents.action_agent import ActionAgent
from agents.manager_agent import ManagerAgent
from database.codebase_database import convert_to_database
from ui.prompts import build_action_prompt, build_manager_prompt
from ui.user_interface import (
    choose_project_source,
    clone_repository,
    display_manager_task_list,
    display_prompt,
    display_task_result,
    display_user_input,
    get_project_folder,
    get_user_input,
    separator,
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


def interaction_loop(manager_agent, action_agent):
    while True:
        user_input = get_user_input()
        display_user_input(user_input)

        task_results = []

        manager_prompt = build_manager_prompt(
            user_input, previous_responses=task_results
        )
        while True:
            task_list = manager_agent.process_input(manager_prompt)

            display_manager_task_list(task_list)

            # Check if the special value (None) is returned, and break the loop if it is
            if task_list is None:
                separator()
                display_prompt("No more tasks to perform", style="bold red")
                break

            for task in task_list:
                action_prompt = build_action_prompt(task)
                task_result = action_agent.process_input(action_prompt)
                task_results.append(task_result)

                display_task_result(task, task_result)

                agent_feedback = format_agent_conversation(task_list, task_results)

                # Send the results back to the Manager Agent for evaluation
                manager_prompt = build_manager_prompt(
                    user_input, previous_responses=agent_feedback
                )

                task_list = manager_agent.process_input(manager_prompt)
                display_manager_task_list(task_list)


def format_agent_conversation(task_list, task_results):
    if task_list is None or task_results is None:
        return None

    formatted_results = []

    min_length = min(len(task_list), len(task_results))

    for index in range(min_length):
        task_result = task_results[index]
        if task_result is None:
            continue

        task = task_list[index]
        for result in task_result:
            task_str = f"Task: {task['task']} ({task['additional_info']})"
            task_thoughts = f"Thoughts: \"{result['thoughts']}\""
            tool_str = f"Tool Used: {result['command']}"
            result_str = f"Tool Result: {result['result']}"

            formatted_result = (
                f"{task_str}\n{task_thoughts}\n{tool_str}\n{result_str}".strip()
            )
            formatted_results.append(formatted_result)

    return "\n\n".join(formatted_results)


if __name__ == "__main__":
    main()
