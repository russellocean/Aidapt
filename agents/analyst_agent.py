import inspect
import json

from agents.agent import Agent
from ui.prompts import build_analyst_prompt


class AnalystAgent(Agent):
    def __init__(self):
        super().__init__()
        self.callback = self.get_callback()
        self.caller_agent = ""
        self.delegated_agent = ""
        self.task = ""
        self.message = ""
        self.project_summary = None
        self.memory = self.get_memory_database()

    def run(self, input_data, delegated_agent=None, task=None, message=None):
        """
        Entry point for the Analyst Agent. The agent
        receives input_data as a JSON object and processes it accordingly.

        Args:
            input_data (dict): a JSON object containing necessary data for task analysis.
        Returns:
            dict: a JSON object containing the refined task details, contextual information,
            and any relevant memory updates.
        """
        self.caller_agent = (
            inspect.currentframe().f_back.f_locals.get("self").__class__.__name__
        )

        self.delegated_agent = delegated_agent
        self.task = task
        self.message = message

        # If the input_data is a string, parse it to a dictionary
        if isinstance(input_data, str):
            input_data = json.loads(input_data)

        formatted_data = self.format_json(input_data)

        prompt = self.build_prompt(formatted_data)

        self.callback("prompt", prompt)

        response = self.process_input(prompt)

        self.project_summary = self.format_project_summary(json_object=response)

        self.callback("info", self.project_summary)

        return self.format_agent_interaction(json_object=response)

    def build_prompt(self, input_data):
        """
        Build the prompt for the Analyst Agent based on the input_data provided.

        Args:
            input_data (dict): a JSON object containing task data, context, and other necessary information.
        Returns:
            str: the prompt to be given to the AI for processing.
        """
        memory_lookup = self.memory.query_memories(f"{self.task} {self.message}")

        prompt = build_analyst_prompt(
            caller_agent=self.caller_agent,
            input_data=input_data,
            project_summary=self.project_summary,
            directed_agent=self.delegated_agent,
            task=self.task,
            message=self.message,
            memory_lookup=memory_lookup,
        )

        return prompt

    def format_agent_interaction(self, json_object):
        formatted_string = ""

        # Agent Interaction Section
        formatted_string += "\nAgent Interaction\n"
        ai_section = json_object["agent_interaction"]
        for key, value in ai_section.items():
            if isinstance(value, dict):
                formatted_string += f"\n\t{key}\n"
                for sub_key, sub_value in value.items():
                    formatted_string += f"\t\t-{sub_key}: {sub_value}\n"
            else:
                formatted_string += f"\n\t-{key}: {value}\n"

        return formatted_string

    def format_project_summary(self, json_object):
        formatted_string = ""

        # Project Summary Section
        formatted_string += "\nProject Summary\n"
        ps_section = json_object["project_summary"]
        for key, value in ps_section.items():
            if key == "project_structure":
                formatted_string += f"\n\t{key}\n"
                for file, file_info in value.items():
                    formatted_string += (
                        f"\t\t{file} (path: {file_info['relative_path']})\n"
                    )
                    formatted_string += (
                        f"\t\t\t-Description: {file_info['description']}\n"
                    )
                    formatted_string += f"\t\t\t-Relations: {file_info['relations']}\n"
                    formatted_string += "\t\t\t-Functions:\n"
                    for function in file_info["functions"]:
                        formatted_string += f"\t\t\t\t-{function['function_name']}: {function['function_description']}\n"
            else:
                formatted_string += f"\n\t-{key}: {value}\n"

        return formatted_string

    def format_json(self, json_object):
        formatted_string = ""

        # Thoughts
        if "thoughts" in json_object:
            formatted_string += f"🧠 Thoughts:\n{json_object['thoughts']}\n"

        # Criticisms
        if "criticisms" in json_object:
            formatted_string += f"💬 Criticisms:\n{json_object['criticisms']}\n"

        # Tools to Run
        if "tools_to_run" in json_object:
            formatted_string += "🛠 Tools to Run:\n"
            for tool in json_object["tools_to_run"]:
                formatted_string += f"- Tool: {tool['tool']}\n"
                if "parameters" in tool:
                    formatted_string += f" Params: {', '.join(tool['parameters'])}\n"

        # Agent Calls
        if "agent_calls" in json_object:
            formatted_string += "📞 Agent Calls:\n"
            for call in json_object["agent_calls"]:
                formatted_string += f"- Agent: {call['agent']}\n  Task: {call['task']}\n  Message: {call['message']}\n"

        # Objective Met
        if "objective_met" in json_object:
            formatted_string += (
                f"✅ Objective Met: {'Yes' if json_object['objective_met'] else 'No'}\n"
            )

        # Final Answer
        if "final_answer" in json_object:
            formatted_string += f"🔚 Final Answer:\n{json_object['final_answer']}\n"

        # Current Task List
        if "current_task_list" in json_object:
            formatted_string += "📋 Current Task List:\n"
            for task in json_object["current_task_list"]:
                formatted_string += f"- Task ID: {task['task_id']}\n  Task: {task['task']}\n  Completed: {'Yes' if task['completed'] else 'No'}\n"

        # Memory Updates
        if "mem_updates" in json_object:
            formatted_string += "💾 Memory Updates:\n"
            for mem_update in json_object["mem_updates"]:
                formatted_string += (
                    f"- Action: {mem_update['action']}\n  Memory Parameters:\n"
                )
                formatted_string += f"- ID: {mem_update['memory_parameters']['id']}\n"
                formatted_string += (
                    f"- Content: {mem_update['memory_parameters']['content']}\n"
                )
                if "metadata" in mem_update["memory_parameters"]:
                    formatted_string += "- Metadata:\n"
                    for key, value in mem_update["memory_parameters"][
                        "metadata"
                    ].items():
                        formatted_string += f"- {key.capitalize()}: {value}\n"

        # Next Task
        if "next_task" in json_object:
            formatted_string += f"➡️ Next Task:\n- Task: {json_object['next_task']['task']}\n  Message: {json_object['next_task']['message']}\n"

        # Result
        if "result" in json_object:
            formatted_string += f"📊 Result:\n{json_object['result']}\n"

        return formatted_string


def main():
    import ast
    import json

    from agents.agent import Agent
    from database.memory_database import MemoryDatabase
    from ui.user_interface import (
        display_intermediate_response,
    )

    # Set the callback for the Agent class, dont set output raw steps to console.
    Agent.set_callback(display_intermediate_response)

    # Create the global memory database.
    memory_database = MemoryDatabase()

    # Set the memory database for the Agent class.
    Agent.set_memory_database(memory_database)

    manager_response = """{
        "thoughts": "The development process will be guided by modern design principles and a focus on user experience. This includes a mobile-first approach, ensuring accessibility for all users, and optimizing for search engine visibility. The tasks will be divided into several specific subtasks, each assigned to an action agent with detailed instructions.",
        "criticisms": "The main challenge is to ensure that the action agent understands the tasks correctly and executes them as expected. The tasks need to be described in a very detailed and specific manner.",
        "tools_to_run": [],
        "agent_calls": [
            {
                "agent": "Action Agent",
                "task": "Create necessary files",
                "message": "Create index.html, style.css, and script.js files in the /User/Dev/Project_folder/ directory",
            },
            {
                "agent": "Action Agent",
                "task": "Write HTML code",
                "message": "Write HTML structure in the index.html file. Use HTML5 semantic elements such as <header>, <nav>, <main>, <section>, <article>, and <footer>. Include a navigation menu in the <header> with links to Home, About, and Contact pages. The <main> should contain a welcome message and a brief introduction to the website. The <footer> should contain copyright information and links to social media profiles.",
            },
            {
                "agent": "Action Agent",
                "task": "Write CSS code",
                "message": "Style the HTML elements in the style.css file. Use a mobile-first approach and ensure that the design is responsive for all screen sizes. Use a simple and clean design with a white background and black text. Style the navigation menu to be horizontal and located at the top of the page. Add a hover effect to the links. Ensure the main content area has a comfortable reading width and the text is easy to read. Position the footer at the bottom of the page and use smaller text.",
            },
            {
                "agent": "Action Agent",
                "task": "Write JavaScript code",
                "message": "Add interactivity to the website in the script.js file. Implement a responsive navigation menu that toggles on and off on smaller screens. Create a carousel for images. Add form validation for any forms on the website.",
            },
        ],
        "objective_met": false,
        "final_answer": "The website is currently under development. Once it is completed and deployed, the final URL will be provided.",
        "current_task_list": [
            {"task_id": 1, "task": "Create necessary files", "completed": false},
            {"task_id": 2, "task": "Write HTML structure", "completed": false},
            {"task_id": 3, "task": "Style HTML elements", "completed": false},
            {
                "task_id": 4,
                "task": "Add interactivity with JavaScript",
                "completed": false,
            },
        ],
        "mem_updates": [
            {
                "action": "add",
                "memory_parameters": {
                    "id": "1",
                    "content": "Website development plan",
                    "metadata": {
                        "project": "website development",
                        "status": "in progress",
                    },
                },
            },
            {
                "action": "add",
                "memory_parameters": {
                    "id": "2",
                    "content": "HTML structure: Use HTML5 semantic elements such as <header>, <nav>, <main>, <section>, <article>, and <footer>. Include a navigation menu in the <header> with links to Home, About, and Contact pages. The <main> should contain a welcome message and a brief introduction to the website. The <footer> should contain copyright information and links to social media profiles.",
                    "metadata": {
                        "project": "website development",
                        "status": "in progress",
                        "task": "HTML structure",
                    },
                },
            },
            {
                "action": "add",
                "memory_parameters": {
                    "id": "3",
                    "content": "CSS styling: Use a mobile-first approach and ensure that the design is responsive for all screen sizes. Use a simple and clean design with a white background and black text. Style the navigation menu to be horizontal and located at the top of the page. Add a hover effect to the links. Ensure the main content area has a comfortable reading width and the text is easy to read. Position the footer at the bottom of the page and use smaller text.",
                    "metadata": {
                        "project": "website development",
                        "status": "in progress",
                        "task": "CSS styling",
                    },
                },
            },
            {
                "action": "add",
                "memory_parameters": {
                    "id": "4",
                    "content": "JavaScript interactivity: Implement a responsive navigation menu that toggles on and off on smaller screens. Create a carousel for images. Add form validation for any forms on the website.",
                    "metadata": {
                        "project": "website development",
                        "status": "in progress",
                        "task": "JavaScript interactivity",
                    },
                },
            },
        ],
    }"""

    def clean_json(str):
        str = (
            str.replace("null", "None")
            .replace("true", "True")
            .replace("false", "False")
        )
        return json.dumps(ast.literal_eval(str))

    manager_response = clean_json(manager_response)

    AnalystAgent().run(
        manager_response,
        delegated_agent="Action Agent",
        task="Write HTML code",
        message="Write HTML structure in the index.html file. Use HTML5 semantic elements such as <header>, <nav>, <main>, <section>, <article>, and <footer>. Include a navigation menu in the <header> with links to Home, About, and Contact pages. The <main> should contain a welcome message and a brief introduction to the website. The <footer> should contain copyright information and links to social media profiles.",
    )


if __name__ == "__main__":
    main()
