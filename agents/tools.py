import os
import re
import subprocess

import requests
import wolframalpha
from dotenv import load_dotenv

from .agent import Agent

# Load the variables from the .env file
load_dotenv()

# Access the variables using the os module
WOLFRAM_API_KEY = os.getenv("WOLFRAM_ALPHA_APPID")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")


def search(query):
    """
    Use Google search to find information related to the query
    and return search results or relevant information.
    """
    url = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}&q={query}"
    response = requests.get(url)
    data = response.json()

    search_items = data.get("items", [])
    results = []
    # print("\nSearch Results:\n" + "-" * 40)
    for idx, search_item in enumerate(search_items):
        title = search_item.get("title")
        link = search_item.get("link")
        result = {"title": title, "link": link}
        results.append(result)

        # print(f"{idx + 1}. {title}\n   {link}\n" + "-" * 40)

    return results


def is_simple_expression(expression):
    """
    Check if the given expression consists of only numbers, arithmetic operators, and parentheses.
    Return True if the expression is simple, otherwise return False.
    """
    return bool(re.match(r"^[\d\+\-\*/\(\)\.\s]*$", expression))


def calculate(expression):
    """
    If the expression is simple, use Python's eval() function to perform the calculation.
    If the expression is complex, use the Wolfram Alpha API to perform the calculation.
    """
    if is_simple_expression(expression):
        try:
            result = eval(expression)
            return str(result)
        except:
            return "Error: Invalid simple arithmetic expression."
    else:
        client = wolframalpha.Client(WOLFRAM_API_KEY)
        try:
            res = client.query(expression)
            result = next(res.results).text
            return result
        except:
            return "Error: Could not calculate the expression using Wolfram Alpha API."


def api_request(api_name, parameters):
    """
    Make a request to the specified API with the given parameters,
    handle the API response, and return the relevant information or actions
    from the API response.
    """
    # Implement the API request functionality as needed, e.g., using requests, etc.
    ...


def git_command(command, parameters):
    """
    Execute the Git command with the specified parameters,
    handle the command output or any errors, and return the command
    output or a summary of the action taken.
    """
    cmd = ["git"] + command.split() + [str(p) for p in parameters.values()]
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode("utf-8")
        return output
    except subprocess.CalledProcessError as e:
        return f"Error: {e.output.decode('utf-8')}"


def create_file(filepath, content):
    """
    Create a new file at the given filepath with the specified content.
    """
    memory_database = Agent.get_memory_database()

    try:
        # Create the directory if it doesn't exist
        dir_name = os.path.dirname(filepath)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        # Create the file
        with open(filepath, "w") as file:
            file.write(content)

        memory_database.add_file_memory(filepath, content)
        return f"Successfully created file at {filepath}"
    except Exception as e:
        return f"Error: {str(e)}"


def delete_file(filepath):
    """
    Delete the file at the given filepath.
    """
    memory_database = Agent.get_memory_database()

    try:
        os.remove(filepath)
        memory_id = f"file-{filepath}"
        memory_database.delete_memory(memory_id)
        return f"Successfully deleted file at {filepath}"
    except FileNotFoundError:
        return f"Error: File not found at {filepath}"
    except Exception as e:
        return f"Error: {str(e)}"


def rename_file(old_filepath, new_filepath):
    """
    Rename the file at the given old_filepath to the new_filepath.
    """
    memory_database = Agent.get_memory_database()

    try:
        os.rename(old_filepath, new_filepath)
        old_memory_id = f"file-{old_filepath}"
        old_file_memory = memory_database.query_memories(id=old_memory_id, top_k=1)
        if old_file_memory:
            content = old_file_memory[0]["metadata"]["content"]
            memory_database.delete_memory(old_memory_id)
            memory_database.add_file_memory(new_filepath, content)
        return f"Successfully renamed file from {old_filepath} to {new_filepath}"
    except FileNotFoundError:
        return f"Error: File not found at {old_filepath}"
    except Exception as e:
        return f"Error: {str(e)}"


def view_file(filepath):
    memory_database = Agent.get_memory_database()

    memory_id = f"file-{filepath}"
    file_memory = memory_database.query_memories(id=memory_id, top_k=1, threshold=0.9)

    if file_memory:
        content = file_memory[0]["metadata"]["content"]
    elif os.path.isfile(filepath):
        with open(filepath, "r") as file:
            content = file.read()
        memory_database.add_file_memory(filepath, content)  # Add file to memory
    else:
        content = f"Error: File memory not found for {filepath}"

    return content


def edit_file(filepath, new_contents):
    memory_database = Agent.get_memory_database()

    memory_id = f"file-{filepath}"
    file_memory = memory_database.query_memories(id=memory_id, top_k=1)  # noqa: F841

    # if file_memory:
    #     # Update the file content in the memory
    #     # Currently update_memory doesn't work, so just use add_file_memory
    #     memory_database.update_memory(
    #         memory_id, new_content=new_contents, new_metadata={"file_path": filepath}
    #     )
    # else:
    # Add a new memory for the file
    memory_database.add_file_memory(filepath, new_contents)

    # Implement the edit functionality as needed, e.g., using regex, parsers, etc.
    with open(filepath, "w") as file:
        file.write(new_contents)


def run_tests(test_command):
    """
    Run tests using the specified test command and return the test results.
    """
    try:
        output = subprocess.check_output(
            test_command.split(), stderr=subprocess.STDOUT
        ).decode("utf-8")
        return output
    except subprocess.CalledProcessError as e:
        return f"Error: {e.output.decode('utf-8')}"
