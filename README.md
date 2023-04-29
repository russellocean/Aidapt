# Codebase Assistant

Codebase Assistant is a powerful tool that helps developers understand, navigate, and improve their codebases using the power of AI. It utilizes the OpenAI GPT-4 API for natural language processing and understanding. The tool provides an interactive, user-friendly interface for developers to seek assistance in various code-related tasks, such as searching for information, viewing and editing files, performing calculations, and interacting with APIs and Git repositories.

## Features

- **Project Source Selection**: Choose between a local folder, a remote Git repository, or no project source.
- **Codebase Analysis**: Convert the project into an AI-friendly database for better context understanding.
- **AI Agent**: Create an AI agent with the necessary tools to assist in various code-related tasks.
- **Interaction Loop**: Interactive user interface that allows for continuous communication between the user and the AI agent.

### Available Commands

- **Search**: Use Google to find information related to a query.
- **ViewFile**: View the content of a file within a directory.
- **EditFile**: Edit files in the codebase based on specified edits.
- **Calculate**: Perform calculations on mathematical expressions.
- **APIRequest**: Make requests to various APIs for specific information or actions.
- **Git**: Utilize Git commands to interact with the codebase repository.

## Installation

1. Make sure you have Python 3.8 or higher installed on your system.
2. Clone the repository:
   ```
   git clone https://github.com/your-username/codebase-assistant.git
   ```
3. Navigate to the project folder:
   ```
   cd codebase-assistant
   ```
4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the `main.py` script:
   ```
   python main.py
   ```
2. Follow the prompts and interact with the AI agent.

### Example Interaction

```
Enter the project source (folder/repository/none): folder
Enter the path to the project folder: path/to/your/project
Enter your objective: How do I create a new class in Python?
```

The AI agent will then provide a detailed response, including the necessary steps, thought process, criticisms, and additional response information to help you achieve your objective.

## Future Goals and Aspirations

- Expand the capabilities of the AI agent to provide more advanced code-related assistance.
- Improve the codebase analysis process for better context understanding.
- Add support for more programming languages and frameworks.
- Implement a web-based user interface for a more seamless and interactive experience.
- Integrate with popular code editors and IDEs to provide real-time assistance.

## Contributing

Contributions are welcome! If you'd like to contribute, please follow these steps:

1. Fork the repository on GitHub.
2. Clone your forked repository to your local machine.
3. Create a new branch for your changes.
4. Make your changes and commit them to your branch.
5. Push your changes to your forked repository on GitHub.
6. Submit a pull request to merge your changes into the main repository.

## License



## Acknowledgements

We would like to thank the OpenAI team for providing the GPT-4 API, which powers the AI agent behind Codebase Assistant.
