import json
import os

import openai
from dotenv import load_dotenv

import ai_agent.langchain_agent  # noqa: F401
from ai_agent.tools import (
    api_request,
    calculate,
    edit_file,
    git_command,
    search,
    view_file,
)
from ui.prompts import build_prompt

# Load the variables from the .env file
load_dotenv()

# Access the variables using the os module
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class AI_Agent:
    def __init__(self, codebase_database=None):
        self.codebase_database = codebase_database

    def create_prompt(self, user_request, context_vector=None):
        prompt = build_prompt(user_request, context_vector)
        return prompt

    def process_input(self, user_request):
        # If there's a codebase database, search for the context vector related to the user request
        if self.codebase_database:
            context_vector = self.codebase_database.search_faiss_index(user_request)
            # Create a prompt for the AI agent using the user request and context vector
            prompt = self.create_prompt(user_request, context_vector)
        # If there's no codebase database, use the user request as the prompt
        else:
            prompt = self.create_prompt(user_request)

        # Ask the AI agent to provide a response for the given prompt
        ai_response = self.ask_agent(prompt)
        # Parse the AI response to obtain commands, parameters, thoughts, criticisms, and additional info
        response_data = self.parse_ai_response(ai_response)

        # If there's a codebase database, execute the commands and update the database
        if self.codebase_database:
            execution_results = self.execute_commands(
                response_data["commands_and_parameters"]
            )
            self.codebase_database.update_faiss_index(execution_results)
            return execution_results, response_data
        # If there's no codebase database, return the AI response directly
        else:
            return response_data

    def ask_agent(self, prompt):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.2,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )

        ai_response = response.choices[0].message.content.strip()
        # print(f"AI response: {ai_response}")
        return ai_response

    def parse_ai_response(self, ai_response):
        try:
            response_data = json.loads(ai_response)
        except json.JSONDecodeError:
            print("Error parsing AI response. Please check the response format.")
            response_data = {}

        # Return a dictionary containing commands_and_parameters, thoughts, criticisms, and additional_info
        return {
            "commands_and_parameters": response_data.get(
                "`commands_and_parameters`", {}
            ),
            "thoughts": response_data.get("thoughts", ""),
            "criticisms": response_data.get("criticisms", ""),
            "additional_info": response_data.get("additional_info", ""),
        }

    def execute_commands(self, commands_and_parameters):
        command_name = commands_and_parameters.get("command")
        parameters = commands_and_parameters.get("parameters", {})

        if command_name in self.available_commands:
            execution_result = self.available_commands[command_name](**parameters)
        else:
            print(
                f"Command '{command_name}' not recognized. Please check the command name."
            )
            execution_result = {}

        return execution_result

    # Define your available commands and corresponding functions here
    available_commands = {
        "Search": search,
        "ViewFile": view_file,
        "EditFile": edit_file,
        "Calculate": calculate,
        "APIRequest": api_request,
        "Git": git_command,
    }
