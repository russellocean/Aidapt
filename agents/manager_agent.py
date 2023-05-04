from ui.prompts import build_manager_prompt

from .agent import Agent


class AgentManager(Agent):
    def __init__(self, users_objective=None):
        super().__init__()
        self.objective_met = False
        self.final_answer = None
        self.users_objective = users_objective
        self.tasks = []

    def run(self, users_objective=None):
        if users_objective is None:
            users_objective = self.users_objective
        else:
            self.users_objective = users_objective
        self.prompt = self.build_prompt()
        self.objective_met = False
        self.final_answer = None

        # Keep processing input and building prompts until the objective is met
        while not self.objective_met:
            print("Current prompt:", self.prompt)  # Print the current prompt
            response = self.process_input(self.prompt)
            print("AI response:", response)  # Print the AI response

            self.process_response(response)

            # Build the next prompt
            self.prompt = self.build_prompt()

        # Once the objective is met, return the final answer
        print(
            "Objective met. Final answer:", self.final_answer
        )  # Print the final answer
        return self.final_answer

    def get_available_tools(self):
        # Define the tools available to the Manager Agent.
        return {
            # Add tool instances here, e.g., 'tool_name': ToolClass()
        }

    def build_prompt(self):
        prompt = build_manager_prompt(
            users_objective=self.users_objective,
            tool_list=self.tools,
            task_list=self.tasks,
        )

        return prompt

    def breakdown_objective(self, objective, memory):
        # Use the Manager Agent to break down the objective into tasks, prioritize them, and assign them to appropriate agents.
        tasks = [
            # Example tasks can be added here, e.g.
            # {"agent": "refactoring", "task": "refactor_code", "message": "Refactor main.py", "completed": False}
        ]
        return tasks

    def process_response(self, response):
        # Update the Manager Agent's state based on the response from other agents.

        # Process the response, update tasks or memory, and check whether the objective has been met.
        thoughts = response.get("thoughts", "")  # noqa: F841
        criticisms = response.get("criticisms", "")  # noqa: F841
        tools_to_run = response.get("tools_to_run", [])
        agent_calls = response.get("agent_calls", [])
        objective_met = response.get("objective_met", False)
        final_answer = response.get("final_answer", "")
        current_task_list = response.get("current_task_list", [])

        # If tools_to_run is not empty (i.e., there are tools to run), execute them.
        self.execute_tools(tools_to_run)

        # Execute any tools specified in the response.
        # for tool in tools_to_run:
        #     tool_name = tool["tool"]
        #     function_name = tool["function"]
        #     parameters = tool["parameters"]
        #     self.execute_tools(tool_name, function_name, parameters)

        # Update the memory and task list based on the agent_calls.
        for agent_call in agent_calls:
            agent_name = agent_call["agent"]
            task_name = agent_call["task"]
            message = agent_call["message"]

            self.delegate_task(agent_name, task_name, message)
            # Update memory and task list as needed, e.g., by adding new tasks or marking tasks as completed.

        # Check if the objective has been met.
        if objective_met:
            self.objective_met = True
            self.final_answer = final_answer

        # Update the task list based on the response's current_task_list.
        # This can be done by comparing the received task list with the manager's task list and updating it accordingly.
        # For example, marking tasks as completed or adding new tasks.
        for task in current_task_list:
            # Update the task list as needed.
            pass

    def perform_task(self, task, message, memory):
        # Override the base class method to provide manager-specific functionality.
        tasks = self.breakdown_objective(message, memory)

        while not self.objective_met:
            for task in tasks:
                if not task["completed"]:
                    agent_name = task["agent"]
                    task_name = task["task"]
                    task_message = task["message"]

                    response = self.delegate_task(
                        agent_name, task_name, task_message, memory
                    )
                    self.process_response(response)

                if self.objective_met:
                    break

        return self.final_answer

    def delegate_task(self, agent_name, task, message):
        # Interact with the AgentManager to delegate tasks to other agents.
        # This method should be called by the AgentManager, which should provide the necessary agent_name, task, message, and memory.
        # The AgentManager can implement a similar method to the one shown in the high-level Python code outline provided earlier.
        pass


def main():
    AgentManager().run("Write a program that prints 'Hello World!' in Python.")


if __name__ == "__main__":
    main()
