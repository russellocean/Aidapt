import os

import openai
from dotenv import load_dotenv
from langchain.embeddings import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()

# Load the variables from the .env file
load_dotenv()

# Access the variables using the os module
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def parse_ai_response(ai_response):
    # Extract commands and parameters from the AI response JSON
    pass


def execute_commands(commands_and_parameters):
    # Execute commands using the available tools and resources
    pass


def get_embedding(text, engine="text-embedding-ada-002"):
    openai.api_key = OPENAI_API_KEY

    query_result = embeddings.embed_query(text)
    return query_result
