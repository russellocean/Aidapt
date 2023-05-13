from ui.prompts import build_action_prompt

from .agent import Agent
from .tools import create_file, edit_file, search


class ActionAgent(Agent):
    def __init__(self):
        super().__init__()
        self.tools = {
            "search": {
                "function": search,
                "description": "Use Google search to find information related to the query and return search results or relevant information.",
                "parameters": ["query"],
            },
            "create_file": {
                "function": create_file,
                "description": "Create a new file at the given filepath with the specified content.",
                "parameters": ["filepath", "content"],
            },
            "edit_file": {
                "function": edit_file,
                "description": "Apply the specified edits to the file at the given filepath, save the file, and return the edited file content or a summary of changes.",
                "parameters": ["filepath", "new_contents"],
            },
        }
        self.callback = self.get_callback()
        self.memory = self.get_memory_database()

    def build_prompt(self, task, message, task_list=None):
        prompt = build_action_prompt(
            task=task,
            message=message,
            memory=self.memory,
            tool_list=self.display_tools(),
            task_list=task_list,
        )

        return prompt

    def perform_task(self, task, message, memory=None, task_list=None):
        # Override the base class method to provide action-specific functionality.

        # Build the prompt for the Action Agent.
        prompt = self.build_prompt(task, message, task_list)
        # self.callback("prompt", prompt)

        # Ask the AI agent using the built prompt.
        response = self.process_input(prompt)

        self.callback("response", response)

        # Parse the AI response, and execute any tools specified.
        if "tools_to_run" in response:
            self.execute_tools(response["tools_to_run"])

        # Update memory based on the AI response.
        if "mem_updates" in response:
            self.update_memory(response["mem_updates"])

        return response["result"]


def main():
    from database.memory_database import MemoryDatabase

    # Set the name of the index to use for the memory database.
    index_name = "codebase-assistant"

    # Create the global memory database.
    memory_database = MemoryDatabase(index_name)

    # Set the memory database for the Agent class.
    Agent.set_memory_database(memory_database)
    ActionAgent().perform_task(
        "Create a main.py file",
        "Put it here: /Users/russellocean/Dev/test, it should print 'Hello, world!'",
    )


if __name__ == "__main__":
    main()
