from agents.tools import (
    calculate,
    create_file,
    delete_file,
    rename_file,
    search,
    view_file,
)
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
            "view_file": {
                "function": view_file,
                "description": "Return the contents of the file at the given filepath.",
                "parameters": ["filepath"],
            },
            "delete_file": {
                "function": delete_file,
                "description": "Delete the file at the given filepath.",
                "parameters": ["filepath"],
            },
            "rename_file": {
                "function": rename_file,
                "description": "Rename the file at the given old_filepath to the new_filepath.",
                "parameters": ["old_filepath", "new_filepath"],
            },
            "calculate": {
                "function": calculate,
                "description": "Calculate the result of the given expression.",
                "parameters": ["expression"],
            },
            "edit_file": {
                "function": edit_file,
                "description": "Apply the specified edits to the file at the given filepath, save the file, and return the edited file content or a summary of changes.",
                "parameters": ["filepath", "new_contents"],
            },
        }
        self.callback = self.get_callback()
        self.memory = self.get_memory_database()
        self.task_list = None

    def build_prompt(self, task, message, task_list=None, task_stack=None):
        prompt = build_action_prompt(
            task=task,
            message=message,
            memory=self.memory,
            tool_list=self.display_tools(),
            task_list=self.task_list,
            task_stack=task_stack,
        )

        return prompt

    def run_task(self, task, message, memory=None, task_list=None, task_stack=None):
        # Override the base class method to provide action-specific functionality.
        self.task_list = task_list

        # Build the prompt for the Action Agent.
        prompt = self.build_prompt(task=task, message=message, task_stack=task_stack)
        self.callback("prompt", prompt)

        # Ask the AI agent using the built prompt.
        response = self.process_input(prompt)

        self.callback("response", response)

        result = self.process_response(response)

        return result

    def process_response(self, response):
        # Extract fields from the response.
        thoughts = response.get("thoughts", "")
        criticisms = response.get("criticisms", "")
        next_task = response.get("next_task", None)
        mem_updates = response.get("mem_updates", [])
        tools_to_run = response.get("tools_to_run", [])
        result = response.get("result", "")

        # Process thoughts and criticisms.
        if thoughts:
            self.callback("thoughts", thoughts)
        if criticisms:
            self.callback("criticisms", criticisms)

        # Process memory updates.
        if mem_updates:
            self.update_memory(mem_updates)

        # Execute tools.
        tool_results = {}
        if tools_to_run:
            tool_results = self.execute_tools(tools_to_run)

        # Process the next task if it exists.
        if next_task:
            task_name = next_task["task"]
            message = next_task["message"]

            task_name = next_task.get("task", "").strip()
            message = next_task.get("message", "").strip()

            task_report = self.build_task_report(
                task_name, message, tool_results, result
            )
            self.callback("task_report", task_report)
            # Checks if task_name and message are not empty strings
            if task_name and message:
                result = self.run_task(
                    task=task_name,
                    message=message,
                    memory=self.memory,
                    task_stack=task_report,
                )

        return result

    def build_task_report(self, task, message, tool_results, result):
        report_lines = [
            f"You previously ran the task '{task}' with the message '{message}'."
        ]

        for (tool, parameters), tool_result in tool_results.items():
            parameters_str = ", ".join(map(str, parameters))
            report_lines.append(
                f"You ran the tool '{tool}' with the parameters '{parameters_str}' which returned the following: '{tool_result}'"
            )

        if result:
            report_lines.append(f"You also provided the result: '{result}'")

        return "\n".join(report_lines)


def main():
    from agents.agent import Agent
    from database.memory_database import MemoryDatabase
    from ui.user_interface import (
        display_intermediate_response,
    )

    # Set the callback for the Agent class, dont set output raw steps to console.
    Agent.set_callback(display_intermediate_response)

    # Set the name of the index to use for the memory database.
    index_name = "codebase-assistant"

    # Create the global memory database.
    memory_database = MemoryDatabase(index_name)

    # Set the memory database for the Agent class.
    Agent.set_memory_database(memory_database)
    ActionAgent().run_task(
        "Modify the main.py file",
        "Modify the main.py file here: /Users/russellocean/Dev/coastal so that the print statement is inside of a main function and is runnable.",
    )


if __name__ == "__main__":
    main()
