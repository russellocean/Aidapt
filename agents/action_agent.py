import json
import re

from .base_agent import Agent
from .tools import (
    calculate,
    create_file,
    edit_file,
    git_command,
    search,
    view_file,
)


class ActionAgent(Agent):
    def __init__(self):
        super().__init__()

    def process_input(self, prompt):
        # Method to execute the task and return the result
        result = self.execute_task(prompt)
        return result

    def execute_task(self, prompt):
        # Logic to execute tasks and return results
        # Example: {"result": "task execution result", "additional_info": "extra context"}
        agent_response = super().ask_agent(prompt)

        # print(f"Action Agent response: {agent_response}")

        # Parse agent_response to obtain commands, parameters, thoughts, criticisms, and additional info
        parsed_responses = self.parse_ai_response(agent_response)

        # Execute the commands and store the results
        executed_commands = []
        for response in parsed_responses:
            commands_and_parameters = response["commands_and_parameters"]
            execution_result = self.execute_commands(commands_and_parameters)
            executed_commands.append(
                {
                    "command": commands_and_parameters["command"],
                    "parameters": commands_and_parameters["parameters"],
                    "result": execution_result,
                    "thoughts": response["thoughts"],
                    "criticisms": response["criticisms"],
                    "additional_info": response["additional_info"],
                }
            )

        return executed_commands

    def parse_ai_response(self, ai_response):
        # Replace single quotes with double quotes within the JSON-like string
        # ai_response = re.sub(r"(\w)'(\w)", r'\1"\2', ai_response)

        # Find all JSON arrays in the AI response
        json_array = re.findall(r"(\[\s*\{.*?\}\s*\])", ai_response, flags=re.DOTALL)

        # print(f"JSON array: {json_array}")

        # If a JSON array is found, parse it
        if json_array:
            try:
                response_data_list = json.loads(json_array[0])
            except json.JSONDecodeError:
                print("Error parsing AI response. Please check the response format.")
                print(f"AI response: {ai_response}")
                response_data_list = []
        else:
            print("Error parsing AI response. Please check the response format.")
            print(f"AI response: {ai_response}")
            response_data_list = []

        # Ensure the response data is a list
        if not isinstance(response_data_list, list):
            response_data_list = [response_data_list]

        # Parse each response in the list
        parsed_responses = []
        for response_data in response_data_list:
            parsed_responses.append(
                {
                    "commands_and_parameters": {
                        "command": response_data.get("command", None),
                        "parameters": response_data.get("parameters", {}),
                    },
                    "thoughts": response_data.get("thoughts", ""),
                    "criticisms": response_data.get("criticisms", ""),
                    "additional_info": response_data.get("additional_info", ""),
                }
            )

        return parsed_responses

    def execute_commands(self, commands_and_parameters):
        command_name = commands_and_parameters.get("command")
        parameters = commands_and_parameters.get("parameters", {})

        if command_name in self.available_commands:
            try:
                execution_result = self.available_commands[command_name](**parameters)
            except TypeError as e:
                print(
                    f"Error executing command: {command_name} with parameters: {parameters}"
                )
                print(f"Exception: {e}")
                execution_result = {
                    "error": f"Failed to execute command '{command_name}' with parameters: {parameters}. Exception: {e}"
                }
        else:
            print(
                f"Command '{command_name}' not recognized. Please check the command name."
            )
            execution_result = {}

        return execution_result

    # Define your available commands and corresponding functions here
    available_commands = {
        "Search": search,
        "ViewFile": view_file,
        "EditFile": edit_file,
        "CreateFile": create_file,
        "Calculate": calculate,
        "Git": git_command,
    }
