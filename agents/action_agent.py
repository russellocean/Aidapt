from ui.prompts import build_action_prompt

from .agent import Agent
from .tools import create_file, search


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
        }
        self.callback = self.get_callback()

    def build_prompt(self, task, message, memory_items):
        prompt = build_action_prompt(
            task=task,
            message=message,
            memory_items=memory_items,
            tool_list=self.display_tools(),
        )

        return prompt

    def perform_task(self, task, message, memory=None):
        # Override the base class method to provide action-specific functionality.

        # Build the prompt for the Action Agent.
        prompt = self.build_prompt(task, message, memory)

        # Ask the AI agent using the built prompt.
        response = self.process_input(prompt)

        self.callback("response", response)

        # Parse the AI response, and execute any tools specified.
        if "tools_to_run" in response:
            self.execute_tools(response["tools_to_run"])

        # Update memory based on the AI response.
        if "mem_updates" in response:
            # self.update_memory(response["mem_updates"], memory)
            print(f"Updated memory: {memory}")

        return response["result"]

    def update_memory(self, mem_updates, memory):
        for mem_update in mem_updates:
            action = mem_update["action"]
            memory_item = mem_update["memory_item"]

            if action == "add":
                memory.append(memory_item)
            elif action == "update":
                # Find the index of the memory item to update.
                index = next(
                    (
                        i
                        for i, item in enumerate(memory)
                        if item["type"] == memory_item["type"]
                    ),
                    None,
                )

                if index is not None:
                    memory[index] = memory_item
            elif action == "delete":
                memory[:] = [
                    item for item in memory if item["type"] != memory_item["type"]
                ]


def main():
    ActionAgent().perform_task(
        "Create a main.py file",
        "Put it here: /Users/russellocean/Dev/test, it should print 'Hello, world!'",
    )


if __name__ == "__main__":
    main()
