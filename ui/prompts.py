import os
from string import Template


def build_manager_prompt(
    users_objective, tool_list=None, task_list=None, execution_responses=None
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

    prompt = read_prompt(
        "prompts.txt",
        "manager_prompt",
        users_objective=users_objective,
        execution_responses=execution_responses,
        tool_list=tool_list,
        task_list=task_list,
    )

    return prompt


def build_action_prompt(
    task, message, memory_items=None, tool_list=None, task_list=None
):
    if memory_items is None:
        memory_items = []
    if tool_list is None:
        tool_list = []

    prompt = read_prompt(
        "prompts.txt",
        "action_prompt",
        task=task,
        message=message,
        memory_items=memory_items,
        tool_list=tool_list,
        task_list=task_list,
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
