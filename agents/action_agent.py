from .base_agent import Agent


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

        print(f"Action Agent response: {agent_response}")

        # Parse agent_response to obtain commands, parameters, thoughts, criticisms, and additional info

        # Execute the commands and return the results

        return agent_response
