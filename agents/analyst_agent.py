from agents.agent import Agent
from ui.prompts import build_analyst_prompt


class AnalystAgent(Agent):
    def __init__(self):
        super().__init__()

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
        self.prompt = self.build_prompt(input_data)
        response = self.process_input(self.prompt)
        return self.process_response(response)

    def build_prompt(self, input_data):
        """
        Build the prompt for the Analyst Agent based on the input_data provided.

        Args:
            input_data (dict): a JSON object containing task data, context, and other necessary information.
        Returns:
            str: the prompt to be given to the AI for processing.
        """
        prompt = build_analyst_prompt(input_data)
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
        # Extract information from the AI's response
        contextual_summary = response.get("contextual_summary", "")
        task_instruction = response.get("task_instruction", "")
        relevant_memory = response.get("relevant_memory", "")
        next_task_instruction = response.get("next_task_instruction", "")
        relevant_code = response.get("relevant_code", "")

        # Build the output JSON object
        output = {
            "contextual_summary": contextual_summary,
            "task_instruction": task_instruction,
            "relevant_memory": relevant_memory,
            "next_task_instruction": next_task_instruction,
            "relevant_code": relevant_code,
        }

        return output

    @staticmethod
    def format_analyst_output(contextual_summary, task_instruction, relevant_memory, next_task_instruction, relevant_code):
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