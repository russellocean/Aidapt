import json
import os

import openai
from dotenv import load_dotenv

# Load the variables from the .env file
load_dotenv()

# Access the variables using the os module
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY


class Agent:
    _callback = None
    _memory_database = None

    def __init__(self):
        self.tools = self.get_available_tools()
        self.callback = self.get_callback()
        self.memory_database = self.get_memory_database()

    def __str__(self):
        tools_str = []
        for tool_name, tool_info in self.tools.items():
            function_description = tool_info["description"]
            parameters = ", ".join(tool_info["parameters"])
            tools_str.append(
                f"{tool_name}: {function_description}\nParameters: {parameters}\n"
            )
        return "\n".join(tools_str)

    @classmethod
    def set_callback(cls, callback):
        cls._callback = callback

    @classmethod
    def get_callback(cls):
        if cls._callback is None:
            return cls.default_callback
        return cls._callback

    @classmethod
    def default_callback(cls, output_type, intermediate_response=None):
        print(f"Output type: {output_type}")
        if intermediate_response is not None:
            print(f"Intermediate response: {intermediate_response}")

    @classmethod
    def set_memory_database(cls, memory_database):
        cls._memory_database = memory_database

    @classmethod
    def get_memory_database(cls):
        return cls._memory_database

    def display_tools(self):
        tools_str = []
        for tool_name, tool_info in self.tools.items():
            function_description = tool_info["description"]
            parameters = ", ".join(tool_info["parameters"])
            tools_str.append(
                f"{tool_name}: {function_description}\nParameters: {parameters}\n"
            )
        return "\n".join(tools_str)

    def get_available_tools(self):
        # Define the tools available to each agent.
        # Each agent can override this method to provide its own tools.
        return []

    def build_prompt(self, task, message, memory):
        # Each agent should override this method to provide its own prompt.
        raise NotImplementedError("build_prompt() should be implemented by each agent.")

    def process_input(self, prompt):
        ai_response = self.ask_agent(prompt)
        return self.parse_response(ai_response)

    def ask_agent(self, prompt):
        response = openai.ChatCompletion.create(
            model="gpt-4",
            temperature=0.2,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )

        ai_response = response.choices[0].message.content.strip()

        return ai_response

    def parse_response(self, ai_response):
        # Replace 'True' and 'False' with 'true' and 'false'
        ai_response = ai_response.replace("True", "true").replace("False", "false")

        # Parse the AI response, which should be in JSON format.
        try:
            parsed_response = json.loads(ai_response)
        except json.JSONDecodeError as e:
            self.callback(
                "error",
                f"doc: {e.doc}, pos: {e.pos}, lineno: {e.lineno}, colno: {e.colno}, message: {e.msg}",
            )
            self.callback(
                "error", f"Error parsing AI response: {e}\n Response: {ai_response}"
            )
            return f"Error parsing AI response, please check the response format. Response provided: {e}"
            # raise ValueError("AI response is not in the expected JSON format.")
        return parsed_response

    def execute_task(self, task, message, memory):
        # Process input, interact with AI, and parse the response.
        response = self.process_input(task, message, memory)

        # If the response contains tools to run, execute them.
        if "tools_to_run" in response:
            self.execute_tools(response["tools_to_run"])

        return response

    def execute_tools(self, tools_to_run):
        for tool_info in tools_to_run:
            tool_name = tool_info["tool"]
            parameters = tool_info["parameters"]

            if tool_name in self.tools:
                tool = self.tools[tool_name]
                function = tool["function"]
                result = function(*parameters)
                self.callback(
                    "tool", f"Tool '{tool_name}' executed with result: {result}"
                )
            else:
                self.callback(
                    "tool", f"Tool '{tool_name}' not available for this agent."
                )

    def perform_task(self, task, message, memory):
        # This is the main method to be called by the AgentManager.
        # It should be implemented by each agent to provide agent-specific functionality.
        raise NotImplementedError("perform_task() should be implemented by each agent.")

    def update_memory(self, mem_updates):
        for mem_update in mem_updates:
            action = mem_update["action"]
            memory_parameters = mem_update["memory_parameters"]

            if action == "add":
                self.memory_database.store_memories([memory_parameters])
            elif action == "update":
                # memory_id = memory_parameters["id"]
                # new_content = memory_parameters.get("content", None)
                # new_metadata = memory_parameters.get("metadata", None)
                # self.memory.update_memory(memory_id, new_content, new_metadata)

                # TODO: Implement this.
                # For now, just overwrite the memory.
                # This is because pinecone update function is not working.
                self.memory_database.store_memories([memory_parameters])
            elif action == "delete":
                memory_id = memory_parameters["id"]
                self.memory_database.delete_memory(memory_id)
