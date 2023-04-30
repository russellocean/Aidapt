import json
import re

from .base_agent import Agent


class ManagerAgent(Agent):
    def __init__(self, codebase_database=None):
        self.codebase_database = codebase_database
        super().__init__()

    def process_input(self, prompt):
        # Method to create and prioritize task lists
        task_list = self.create_and_prioritize_task_list(prompt)
        return task_list

    def create_and_prioritize_task_list(self, prompt):
        agent_response = super().ask_agent(prompt)

        print(f"Agent response: {agent_response}")

        # Replace single quotes with double quotes within the JSON-like string
        agent_response = re.sub(r"(\w)'(\w)", r'\1"\2', agent_response)

        # Find all JSON arrays in the agent_response
        json_array = re.findall(r"(\[\s*\{.*?\}\s*\])", agent_response, flags=re.DOTALL)

        # If a JSON array is found, parse it
        if json_array:
            try:
                task_list = json.loads(json_array[0])
            except json.JSONDecodeError:
                print("Error parsing agent response. Please check the response format.")
                print(f"Agent response: {agent_response}")
                task_list = []
        else:
            print("Error parsing agent response. Please check the response format.")
            print(f"Agent response: {agent_response}")
            task_list = []

        # Check if "results" is present in the task_list
        if task_list and "results" in task_list[0]:
            # Return a special value (None) to signify the loop should be done
            return None

        # Sort the task list based on priority
        task_list.sort(key=lambda x: x["priority"])

        return task_list
