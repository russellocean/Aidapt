import os

import openai
from dotenv import load_dotenv

# Load the variables from the .env file
load_dotenv()

# Access the variables using the os module
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY


class Agent:
    def __init__(self):
        pass

    def process_input(self, user_input):
        raise NotImplementedError(
            "process_input method must be implemented in the derived class"
        )

    def execute_task(self, task):
        raise NotImplementedError(
            "execute_task method must be implemented in the derived class"
        )

    def ask_agent(self, prompt):
        response = openai.ChatCompletion.create(
            model="gpt-4",
            temperature=0.2,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )

        ai_response = response.choices[0].message.content.strip()
        return ai_response

    def parse_ai_response(self, ai_response):
        pass
