from operators.github_file_read import GitHubFileReader
from mock_ai_context import MockAiContext
from operators.ask_chatgpt import AskChatGpt
import os


def GenerateMainDocumentation(repo_info):
    ai_context = MockAiContext()
    GitHubFileReader().run_step(repo_info, ai_context)
    file_names = ai_context.get_output("file_names")
    file_contents = ai_context.get_output("file_contents")  
    
    with open("TestDocs/RepoContent.txt", "w", encoding='utf-8') as f:
        for i in range(len(file_names)):
            f.write(f"{file_names[i]}:\n")
            f.write(file_contents[i]+ "\n")
            f.write('-----------------------------------------------------------\n')

    instructions = "As a Senior Back-end Developer, your task is to generate a comprehensive README documentation for the given repository. Below is a representation of several files within this repository. Each file is depicted by its name, followed by a colon (:), then its content. Files are separated by a line of dashes (-----------------------------------------------------------). Kindly analyze the files and create a well-structured README documentation to be uploaded to the repository."
    instructions2= """As a Senior Back-end Developer, your task is to generate comprehensive README documentation for the given repository. Below is a representation of several files within this repository. Each file is depicted by its name, followed by a colon (:), then its content. Files are separated by a line of dashes (-----------------------------------------------------------). Kindly analyze the files and create well-structured README documentation to be uploaded to the repository.

Please ensure the documentation is organized into the following sections:

Project Title: A concise and descriptive title for the project.
Introduction: A brief overview of the project and its objectives.
Technologies Used: List and brief descriptions of the technologies, frameworks, and libraries used.
Installation: Step-by-step instructions on how to get the environment set up and running.
Endpoints: Description of the API endpoints (if any) with examples of requests and responses.
Ensure that each section is well-detailed and provides sufficient information for readers to understand the project, its setup, and usage.

"""
    with open("TestDocs/RepoContent.txt", "r", encoding='utf-8') as f:
        file_text = f.read()

    
    ai_context.set_input("question", file_text)
    ai_context.set_input("context", "The following is the content of the files in the repository:")
    

    prompt_info = {
        "parameters": {
            "question": "",
            "context": "",
            "function": ""
        },
    }
    
    AskChatGpt().run_step(prompt_info, instructions, ai_context)
    response = ai_context.get_output("chatgpt_response")
    print(response)
    with open("TestDocs/README.md", "w", encoding='utf-8') as f:
        f.write(response)

    return "Files read successfully!"
