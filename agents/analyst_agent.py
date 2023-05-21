import inspect

from agents.agent import Agent
from ui.prompts import build_analyst_prompt


class AnalystAgent(Agent):
    def __init__(self):
        super().__init__()
        self.callback = self.get_callback()

    def run(self, input_data):
        """
        Entry point for the Analyst Agent. The agent
        receives input_data as a JSON object and processes it accordingly.

        Args:
            input_data (dict): a JSON object containing necessary data for task analysis.
        Returns:
            dict: a JSON object containing the refined task details, contextual information,
            and any relevant memory updates.
        """
        agent_name = (
            inspect.currentframe().f_back.f_locals.get("self").__class__.__name__
        )
        prompt = self.build_prompt(input_data, agent_name)

        self.callback("prompt", prompt)

        response = self.process_input(prompt)

        self.callback("analyst", response)

        return self.process_response(response)

    def build_prompt(self, input_data, agent_name):
        """
        Build the prompt for the Analyst Agent based on the input_data provided.

        Args:
            input_data (dict): a JSON object containing task data, context, and other necessary information.
        Returns:
            str: the prompt to be given to the AI for processing.
        """

        print(f"Caller class name: {agent_name}")

        prompt = build_analyst_prompt(input_data, agent_name)
        return prompt

    def process_response(self, response):
        """
        Process the AI's response and format the output JSON object.

        Args:
            response (str): the AI's response to the prompt.
        Returns:
            dict: a JSON object containing the refined task details, contextual information,
            and any relevant memory updates.
        """
        # Define the required keys
        required_keys = [
            "contextual_summary",
            "task_instruction",
            "relevant_memory",
            "next_task_instruction",
            "relevant_code",
        ]

        # Initialize an empty output dictionary
        output = {}

        # Check if the key is in the response, if it is then include it in the output
        for key in required_keys:
            if key in response:
                # Extract information from the AI's response and add it to the output
                output[key] = response.get(key, "")

        return output

    @staticmethod
    def format_analyst_output(
        contextual_summary,
        task_instruction,
        relevant_memory,
        next_task_instruction,
        relevant_code,
    ):
        """
        Format the Analyst Agent's output as a single string.

        Args:
            contextual_summary (str): a high-level summary of the current situation.
            task_instruction (str): the specific task to be accomplished.
            relevant_memory (str): past information that might be useful for the task.
            next_task_instruction (str): the proposed next step based on the task instruction.
            relevant_code (str): any piece of code that's relevant to the task.
        Returns:
            str: the formatted output string.
        """
        output = f"Contextual Summary: {contextual_summary}\n"
        output += f"Task Instruction: {task_instruction}\n"
        output += f"Relevant Memory: {relevant_memory}\n"
        output += f"Next Task Instruction: {next_task_instruction}\n"
        output += f"Relevant Code: {relevant_code}"
        return output


def main():
    from agents.agent import Agent
    from ui.user_interface import (
        display_intermediate_response,
    )

    # Set the callback for the Agent class, dont set output raw steps to console.
    Agent.set_callback(display_intermediate_response)

    # Currently not using memory
    # Set the name of the index to use for the memory database.
    # index_name = "codebase-assistant"

    # Create the global memory database.
    # memory_database = MemoryDatabase(index_name)

    # Set the memory database for the Agent class.
    # Agent.set_memory_database(memory_database)

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

    AnalystAgent().run(manager_response)


if __name__ == "__main__":
    main()
