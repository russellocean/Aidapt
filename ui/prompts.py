import os
from string import Template


def build_manager_prompt(
    users_objective,
    tool_list=None,
    task_list=None,
    execution_responses=None,
    memory=None,
):
    if tool_list is None:
        tool_list = "No tools available."
    if task_list is None:
        task_list = "No tasks yet."
    if execution_responses is not None:
        execution_responses = (
            "\nThe previous response's from your agent calls were: "
            + " ".join(str(x) for x in execution_responses)
        )
    else:
        execution_responses = ""

    relevant_memories = memory.query_relevant_memories(task=task_list, message="")

    if len(relevant_memories) > 0:
        memory_prompt = "Relevant memories found:\n" + "\n".join(relevant_memories)
    else:
        memory_prompt = "No relevant memories were found."

    prompt = read_prompt(
        "prompts.txt",
        "manager_prompt",
        users_objective=users_objective,
        execution_responses=execution_responses,
        memory_prompt=memory_prompt,
        tool_list=tool_list,
        task_list=task_list,
        memory=memory,
    )

    return prompt


def build_action_prompt(information, tool_list=None):
    prompt = read_prompt(
        "prompts.txt",
        "action_prompt",
        analyst_info=information,
        tool_list=tool_list,
    )

    return prompt


def build_analyst_prompt(
    caller_agent,
    input_data,
    project_summary=None,
    directed_agent=None,
    task=None,
    message=None,
    memory_lookup=None,
):
    if project_summary is None:
        project_summary = "No project summary available."
    if directed_agent is None:
        directed_agent = caller_agent
    if task is None:
        task = "No task available."
    if message is None:
        message = "No message available."
    if memory_lookup is None:
        memory_lookup = "No memory provided."

    prompt = read_prompt(
        "prompts.txt",
        "analyst_prompt",
        caller_agent=caller_agent,
        input_data=input_data,
        project_summary=project_summary,
        directed_agent=directed_agent,
        task=task,
        message=message,
        memory_lookup=memory_lookup,
    )

    return prompt


def read_prompt(file_path, prompt_name, **variables):
    parent_dir = os.path.abspath(os.path.join(__file__, "../../"))
    prompts_path = os.path.join(parent_dir, file_path)
    with open(prompts_path, "r") as file:
        content = file.read()
        prompt_start = content.index(f"[{prompt_name}]") + len(prompt_name) + 2
        prompt_end = content.index("[end]", prompt_start)
        prompt_template = content[prompt_start:prompt_end]
        template = Template(prompt_template)
        prompt = template.substitute(variables)
        return prompt
