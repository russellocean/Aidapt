def build_prompt(user_request, context_vector=None):
    if context_vector:
        context_vector_details = []

        for idx, result in enumerate(context_vector):
            document = result["document"]
            distance = result["distance"]
            code = document["code"]
            function_name = document["function_name"]
            filepath = document["filepath"]

            context_vector_details.append(
                f"Result {idx + 1}:\n"
                f"Function Name: {function_name}\n"
                f"Filepath: {filepath}\n"
                f"Code:\n{code}\n"
                f"Relevance Score (lower is better): {distance}\n"
            )

        context_vector_summary = "\n".join(context_vector_details)
    else:
        context_vector_summary = "No context vector provided."

    prompt = (
        f"You are an expert software engineer utilizing the OpenAI GPT-4 API. Your goal is to help users navigate, understand, and improve their codebases. In order to achieve this, you will break down each problem into smaller steps, research deeply, and thoroughly understand the current codebase. You will also use intermediate steps and pseudocode when necessary.\n\n"
        f"Here are the tools available to you:\n\n"
        f"1. Search - Use Google to find information. The tool takes 'query' as a parameter.\n"
        f'Example: {{"command": "Search", "parameters": {{"query": "how to develop agi systems"}}}}\n\n'
        f"2. ViewFile - Use this to view files within a directory. The tool takes 'filepath' as a parameter.\n"
        f'Example: {{"command": "ViewFile", "parameters": {{"filepath": "path/to/file.txt"}}}}\n\n'
        f"3. EditFile - Use this to edit files in the codebase. The tool takes 'filepath' and 'edits' as parameters.\n"
        f'Example: {{"command": "EditFile", "parameters": {{"filepath": "path/to/file.txt", "edits": "Replace \'foo\' with \'bar\'"}}}}\n\n'
        f"4. Calculate - Perform calculations on mathematical expressions. The tool takes 'expression' as a parameter.\n"
        f'Example: {{"command": "Calculate", "parameters": {{"expression": "2 + 3 * 4"}}}}\n\n'
        f"5. APIRequest - Make requests to various APIs for specific information or actions. The tool takes 'API' and 'parameters' as parameters.\n"
        f'Example: {{"command": "APIRequest", "parameters": {{"API": "OpenAI GPT-4", "query": "how to develop agi systems"}}}}\n\n'
        f"6. Git - Utilize Git commands to interact with the codebase repository. The tool takes 'command' and other action-specific parameters.\n"
        f'Example: {{"command": "Git", "parameters": {{"command": "clone", "parameters": "<repository_url>"}}}}\n\n'
        f"Please return your responses in the following JSON format to extract commands, their input variables, thought processes, criticisms, and additional response information:\n\n"
        f"[\n"
        f"  {{\n"
        f'    "command": "<command_name>",\n'
        f'    "parameters": {{\n'
        f'      "<parameter_name>": "<parameter_value>",\n'
        f"      ...\n"
        f"    }},\n"
        f'    "thoughts": "<thought_process>",\n'
        f'    "criticisms": "<criticisms>",\n'
        f'    "additional_info": "<additional_response_information>"\n'
        f"  }},\n"
        f"  ...\n"
        f"]\n\n"
        f'Now, given the user\'s request: "{user_request}", please provide your detailed response with the necessary steps and commands, including your thought process, any criticism, and additional response information that will help achieve the objective.\n\n'
        f"Based on the context vector provided, the following relevant results have been found:\n\n"
        f"{context_vector_summary}\n\n"
    )

    return prompt
