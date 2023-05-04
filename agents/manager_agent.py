from agents.action_agent import ActionAgent
from ui.prompts import build_manager_prompt

from .agent import Agent


class AgentManager(Agent):
    def __init__(self, users_objective=None):
        super().__init__()
        self.objective_met = False
        self.final_answer = None
        self.users_objective = users_objective
        self.tasks = []
        self.callback = self.get_callback()

    def run(self, users_objective=None, confirmation=False):
        if users_objective is None:
            users_objective = self.users_objective
        else:
            self.users_objective = users_objective
        self.prompt = self.build_prompt()

        self.objective_met = False
        self.final_answer = None

        # Keep processing input and building prompts until the objective is met or the user stops the process
        while not self.objective_met:
            response = self.process_input(self.prompt)

            self.callback("response", response)

            # If confirmation is required, ask the user if they want to continue
            if confirmation:
                user_input = self.callback("continuation")
                if user_input != "yes":
                    self.callback("info", "Process stopped by user.")
                    break
            else:
                self.callback(
                    "warning",
                    "Confirmation mode is not enabled. Continuous mode is on.",
                )

            self.process_response(response)

            # Check if the objective has been met
            if self.objective_met:
                break

            # Build the next prompt
            self.prompt = self.build_prompt()

        # Once the loop ends, return the final answer (if the objective has been met)
        if self.objective_met:
            self.callback("final_answer", self.final_answer)
            return self.final_answer
        else:
            self.callback("final_answer", "No answer found.")
            return None

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

    def process_response(self, response):
        # Update the Manager Agent's state based on the response from other agents.

        # Process the response, update tasks or memory, and check whether the objective has been met.
        thoughts = response.get("thoughts", "")  # noqa: F841
        criticisms = response.get("criticisms", "")  # noqa: F841
        tools_to_run = response.get("tools_to_run", [])
        agent_calls = response.get("agent_calls", [])
        objective_met = response.get("objective_met", False)
        final_answer = response.get("final_answer", "")
        current_task_list = response.get("current_task_list", self.tasks)

        # If tools_to_run is not empty (i.e., there are tools to run), execute them.
        self.execute_tools(tools_to_run)

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

        updated_tasks = []

        # Iterate through the tasks in the response's current_task_list
        for task in current_task_list:
            task_id = task["task_id"]

            # Search for the task_id in the manager's task list
            existing_task = next(
                (t for t in self.tasks if t["task_id"] == task_id), None
            )

            if existing_task is None:
                # If the task_id is not in the manager's task list, add the task
                updated_tasks.append(task)
            else:
                # Update the task's completion status and add it to the updated_tasks list
                existing_task["completed"] = task["completed"]
                updated_tasks.append(existing_task)

        # Set self.tasks to the updated_tasks list
        self.tasks = updated_tasks
        # print(f"Updated tasks: {self.tasks}")
        self.callback("tasks", self.tasks)

    def delegate_task(self, agent_name, task, message):
        # Interact with the AgentManager to delegate tasks to other agents.
        # This method should be called by the AgentManager, which should provide the necessary agent_name, task, message, and memory.
        # The AgentManager can implement a similar method to the one shown in the high-level Python code outline provided earlier.
        result = None

        normalized_agent_name = normalize_agent_name(agent_name)

        if normalized_agent_name == "actionagent":
            self.callback("delegating", f"delegating task {task} to {agent_name}.")
            result = ActionAgent().perform_task(task, message)
        else:
            self.callback("delegating", f"Agent {agent_name} is not supported.")
            result = f"Agent {agent_name} is not supported."

        # Add other agents here as needed.
        return result


def normalize_agent_name(agent_name):
    return agent_name.strip().replace(" ", "").replace("_", "").lower()


def format_response(response):
    formatted_response = ""

    formatted_response += "Thoughts:\n"
    formatted_response += response["thoughts"] + "\n\n"

    if response["criticisms"]:
        formatted_response += "Criticisms:\n"
        formatted_response += response["criticisms"] + "\n\n"

    if response["tools_to_run"]:
        formatted_response += "Tools to run:\n"
        for tool in response["tools_to_run"]:
            formatted_response += f"  - Tool: {tool['tool']}\n"
            formatted_response += f"    Parameters: {', '.join(tool['parameters'])}\n"
        formatted_response += "\n"

    if response["agent_calls"]:
        formatted_response += "Agent Calls:\n"
        for agent_call in response["agent_calls"]:
            formatted_response += f"  - Agent: {agent_call['agent']}\n"
            formatted_response += f"    Task: {agent_call['task']}\n"
            formatted_response += f"    Message: {agent_call['message']}\n"
        formatted_response += "\n"

    formatted_response += (
        f"Objective Met: {'Yes' if response['objective_met'] else 'No'}\n"
    )

    if response["final_answer"]:
        formatted_response += "Final Answer:\n"
        formatted_response += response["final_answer"] + "\n\n"

    if response["current_task_list"]:
        formatted_response += "Current Task List:\n"
        for task in response["current_task_list"]:
            formatted_response += f"  - Task ID: {task['task_id']}\n"
            formatted_response += f"    Task: {task['task']}\n"
            formatted_response += (
                f"    Completed: {'Yes' if task['completed'] else 'No'}\n"
            )
        formatted_response += "\n"

    return formatted_response


def main():
    AgentManager().run(
        "Write a program that prints 'Hello World!' in Python at this directory: /Users/russellocean/Dev/test. Delegalte the task to the ActionAgent.",
        confirmation=True,
    )


if __name__ == "__main__":
    main()
