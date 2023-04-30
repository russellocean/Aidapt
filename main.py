from ai_agent.ai_agent import AI_Agent
from database.codebase_database import convert_to_database
from ui.user_interface import (
    choose_project_source,
    clone_repository,
    display_response_table,
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
    codebase_database = convert_to_database(project_folder, project_source)

    # Step 3: Create AI agent with necessary tools
    ai_agent = AI_Agent(codebase_database)

    # Step 4: Begin interaction loop between user and AI agent
    interaction_loop(ai_agent)


def interaction_loop(ai_agent):
    previous_responses = []
    user_input = get_user_input()
    print(f"User input: {user_input}")

    while True:
        # Process the user input and perform the requested action using the AI agent
        execution_results_list, ai_responses = ai_agent.process_input(
            user_input, previous_responses
        )

        formatted_ai_responses = format_ai_responses(ai_responses)
        formatted_execution_results_list = format_execution_results_list(
            execution_results_list
        )

        final_answer = None

        # Display the AI response to the user and check for a final answer
        for ai_response in ai_responses:
            display_response_table(ai_response)
            print("\n")

            if "final_answer" in ai_response:
                final_answer = ai_response["final_answer"]
                break

        if final_answer is not None:
            print(f"Final Answer: {final_answer}")
            break

        # Store the formatted_ai_responses and formatted_execution_results_list to be used in the next iteration
        previous_responses = formatted_ai_responses + formatted_execution_results_list


def format_ai_responses(ai_responses):
    formatted_ai_responses = []
    for ai_response in ai_responses:
        # Format the ai_response as needed
        formatted_ai_response = {
            "commands_and_parameters": ai_response["commands_and_parameters"],
            "thoughts": ai_response["thoughts"],
            "criticisms": ai_response["criticisms"],
            "additional_info": ai_response["additional_info"],
        }
        if "final_answer" in ai_response:
            formatted_ai_response["final_answer"] = ai_response["final_answer"]

        formatted_ai_responses.append(formatted_ai_response)
    return formatted_ai_responses


def format_execution_results_list(execution_results_list):
    def format_value(value):
        if isinstance(value, dict):
            return {k: format_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [format_value(v) for v in value]
        else:
            return value

    formatted_execution_results_list = []
    for execution_results in execution_results_list:
        # Format the execution_results as needed
        formatted_execution_results = format_value(execution_results)
        formatted_execution_results_list.append(formatted_execution_results)

    return formatted_execution_results_list


if __name__ == "__main__":
    main()
