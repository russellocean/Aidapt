# Aidapt Codebase Assistant

The Aidapt Codebase Assistant is an advanced software application designed to assist developers in understanding, maintaining, and improving codebases using natural language input. The primary goal of this project is to create an intelligent agent system that works alongside developers to help them navigate complex codebases, refactor code, implement new features, and perform various programming tasks.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Agent Overview](#agent-overview)
  - [Manager Agent](#manager-agent-overview)
  - [Action Agent](#action-agent-overview)
  - [Analyst Agent (Work in progress)](#analyst-agent-overview)
- [File Structure](#file-structure)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/russellocean/aidapt.git
```

2. Change into the project directory:

```bash
cd aidapt
```

3. (Optional) Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

4. Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

To run the Aidapt Codebase Assistant, execute the following command:

```bash
python main.py
```

Provide a natural language query or task through the user interface, and the Aidapt system will assist you with your codebase-related task.

## Agent Overview

The Aidapt system consists of three primary agents:

1. [Manager Agent](#manager-agent-overview): Responsible for understanding the user's objectives, developing plans, assigning tasks to other agents, tracking progress, handling unexpected events, and maintaining communication with the user.
2. [Action Agent](#action-agent-overview): Executes tasks assigned by the Manager Agent and improved by the Analyst Agent. Performs actions and implements solutions.
3. [Analyst Agent (Work in progress)](#analyst-agent-overview): Analyzes tasks and context, refines instructions, and provides feedback to the Manager and Action Agents.

---

### Manager Agent Overview

#### Description
The Manager Agent is the orchestrator in the Aidapt system. It understands the user's objectives, develops plans, assigns tasks to other agents, tracks progress, handles unexpected events, and maintains communication with the user. While the Manager Agent doesn't perform the tasks itself, it plays a crucial role in ensuring that the tasks are executed correctly and efficiently. The Manager Agent also integrates the outputs from the Analyst Agent, using them to refine instructions, improve context, and guide the other agents more effectively.
#### Primary Functions
The Manager Agent is responsible for several key functions:

- **Task Allocation:** The Manager Agent determines and assigns the tasks that need to be accomplished. It selects tasks based on priority, feasibility, and the overall goals of the Aidapt system.
- **Agent Coordination:** The Manager Agent facilitates coordination among the various agents in the system, ensuring seamless communication and efficient task execution.
- **Monitoring and Evaluation:** The Manager Agent oversees the performance of the other agents and the outcomes of the tasks, evaluating progress and ensuring objectives are met.
- **System Optimization:** Based on task outcomes and agent performance, the Manager Agent continually adjusts strategies and processes to optimize overall system performance.

#### Example Iteration Loop
1. User provides a task to the Manager Agent.
2. Manager Agent creates a plan and assigns tasks to the Action Agent.
3. Before tasks are executed, the Analyst Agent steps in to refine the instructions and context.
4. Action Agent executes the task based on the refined instructions.
5. The output from the Action Agent is then processed by the Analyst Agent, which analyzes the results, identifies issues, and provides further instructions or context if necessary.
6. This process is repeated until all tasks are completed, with the Manager Agent monitoring progress and making adjustments as needed.

#### Reasoning and Functionality
The Manager Agent is designed to be the central control unit in the Aidapt system. It manages the workflow, ensures that tasks are completed correctly, and maintains communication with the user. The iterative nature of the Manager Agent, combined with the input from the Analyst Agent, allows for effective management of complex, multi-stage tasks.

---

### Action Agent Overview
The Action Agent is a pivotal component of the Aidapt system, designed to execute tasks assigned by the Manager Agent and improved by the Analyst Agent. The Action Agent is directly responsible for implementing actions in a practical and adaptable manner.

#### Purpose and Function
- The Action Agent's primary function is **to perform tasks as instructed**. These tasks can span a wide range of complexities, from running software tools to writing code.
- The Action Agent works in an **iterative cycle**, carrying out one part of a larger task during each iteration. It does not remember past actions; instead, it solely acts based on the instruction and context provided at the moment.
- **Action Plan Execution**: The Action Agent follows a detailed action plan, interpreting the task, using available tools, updating shared memory, and communicating its progress and potential issues.

#### Task Iteration Loop
1. The Manager Agent generates a task list and selects a task to be executed by the Action Agent.
2. The Analyst Agent then receives this task, refines the context and instructions, and passes it on to the Action Agent.
3. The Action Agent interprets the task and executes it. For multi-stage tasks, the agent will determine the next necessary action. For example, if the task is to modify a specific file, the first action might be to view the file.
4. The Analyst Agent receives the output of the Action Agent, analyzes it, and refines the instructions for the next step based on the current result.
5. The Action Agent then carries out the next step in the task.
6. This loop continues until the entire task is completed. The final output is then sent to the Manager Agent through the Analyst Agent, which ensures the output is in an optimal format and that all elements of the task have been addressed.

#### Reasoning and Functionality
The Action Agent is designed to be the 'doer' in the Aidapt system. It takes instructions and performs tasks, acting as the primary executor. The iterative nature of the Action Agent allows it to handle complex, multi-stage tasks by breaking them down into manageable parts. The Action Agent's functionality is enhanced by the Analyst Agent, which refines instructions and context to ensure optimal task execution.

---

### Analyst Agent Overview

- Analyst Agent is currently under development and will be updated in the future.

The Analyst Agent is a crucial component in the AI agent ecosystem. It serves as an intermediary between other agents, particularly the Manager and Action Agents, ensuring that tasks are executed optimally and efficiently.


#### Purpose and Function
The Analyst Agent performs several key functions:

- **Contextual Understanding:** The Analyst Agent is responsible for understanding the current situation, task, and other relevant details from the Manager Agent or Action Agent.
- **Task Refinement:** Based on its understanding, the Analyst Agent refines the task details, providing clearer instructions, highlighting relevant information, and suggesting next steps.
- **Data Processing:** The Analyst Agent processes and presents only the necessary data to the Action Agent, reducing noise and improving focus on the task at hand.
- **Result Analysis:** After an Action Agent completes a task, the Analyst Agent analyzes the result, ensuring the task objectives are met and providing a summary of the work done.
- **Feedback to the Manager Agent:** The Analyst Agent also communicates results, possible issues, and suggestions for improvement back to the Manager Agent, aiding in decision-making and planning.

#### Reasoning and Functionality

The Analyst Agent is designed to act as a 'smart filter' and 'task refiner' in the agent ecosystem. Given that the Action Agent has no memory of past actions and only acts on the information provided in its current turn, the Analyst Agent plays a critical role in maintaining context, ensuring task clarity, and improving overall execution efficiency.

## File Structure
```
Aidapt
 ┣ agents
 ┃ ┣ action_agent.py
 ┃ ┣ agent.py
 ┃ ┣ manager_agent.py
 ┃ ┗ tools.py
 ┣ database
 ┃ ┣ codebase_database.py
 ┃ ┣ file_parser.py
 ┃ ┗ memory_database.py
 ┣ tests
 ┃ ┣ test_embedding.py
 ┃ ┗ test_tools.py
 ┣ ui
 ┃ ┣ prompts.py
 ┃ ┗ user_interface.py
 ┣ .gitignore
 ┣ LICENSE
 ┣ main.py
 ┣ prompts.txt
 ┗ utils.py
```

## Contributing

Contributions are welcome! Feel free to submit a pull request or open an issue to discuss improvements or additions to the Aidapt Codebase Assistant.

## License

This project is licensed under the GPL License. See the [LICENSE](LICENSE) file for more information.
