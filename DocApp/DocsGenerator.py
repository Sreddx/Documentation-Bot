from operators.ask_chatgpt import AskChatGpt
from operators.github_file_read import GitHubFileReader
from operators.github_docs_writer import GitHubDocsWriter
from mock_ai_context import MockAiContext

def check_regex_with_repo(repo_info):
    # Create mock ai context
    test_ai_context = MockAiContext()
    

    # Get repo file names and contents into ai context
    GitHubFileReader().retrieve_github_files(repo_info, test_ai_context)
    return test_ai_context.get_output("matching_files")

    

    

def generate_docs(ai_context,context,repo_name, folders, file_regex, branch):
    
    # Create dictionary for repo_info
    repo_info = {
        "parameters": {
            "repo_name": repo_name,
            "folders": folders,
            "file_regex": file_regex,
            "branch": branch
        },
    }
    # Create dictionary for prompt info
    prompt_info = {
        "parameters": {
            "question": "Generate Markdown documentation for this code. This documentation is meant to summarize the purpose and technical details of this code file.Use headings to breakdown the documentation into the following sections: Summary: A one sentence summary of this component's functionality. Inputs: briefly describe the inputs and their purpose. Dependencies: briefly describe dependencies and their purpose. Functions: brief summary of functions present in the code. Requests: in case the code sends request to an API or something outside of the application describe the request including headers, parameters and payload. Outputs: briefly describe outputs and their purpose.",
            "function": ""
        },
    }
    

    # Get repo file names and contents into ai context
    
    GitHubFileReader().run_step(repo_info, ai_context)
    
    num_files_to_read = len(ai_context.get_output("file_names"))
    docs = {}
    
    

    # Generate documentation for each file
    for i in range(num_files_to_read):
        ai_context.set_input("context", context)
        ai_context.set_input("question", prompt_info["parameters"]["question"] + "- The following code is the file Content:" + ai_context.get_output("file_contents")[i])
        try:
            AskChatGpt().run_step(prompt_info, ai_context)
            docs[ai_context.get_output("file_names")[i]] = ai_context.get_output("chatgpt_response")
        except Exception as e:
            print("Error in generating documentation for file: " + ai_context.get_output("file_names")[i])
            print(str(e))
            continue
    print(f'Documentation generated for {num_files_to_read} files successfully!')

    

    # Save the documentation in TestDocs folder
    try:
        for file_name, file_content in docs.items():
            with open("TestDocs/" + file_name.replace("/", "_") + ".md", "w") as f:
                f.write(file_content)
    except Exception as e:
        print("Error in saving documentation to TestDocs folder:" + str(e))
    return docs


def add_docs_to_repo(context,repo_name, folders, file_regex, branch, docs_folder_name):
    """
    This function generates documentation for a repo and adds the docs back to a specified folder 
    in the repo.

    Parameters:
    - context (string): string containing the prompt context.
    - repo_name (str): The name of the GitHub repository.
    - docs_folder_name (str): The name of the folder where the generated docs will be added.

    Returns:
    - Success message if the docs are added successfully.
    """
    ai_context = MockAiContext()
    try:
        # Generate the documentation using the generate_docs function
        docs = generate_docs(ai_context,context, repo_name, folders, file_regex, branch)
    except Exception as e:
        print("Error in generating docs: " + str(e))
        return str(e)
    # Prepare the data for the GitHubDocsWriter operator
    file_names = [f"{docs_folder_name}/{name.replace('/', '_')}.md" for name in docs.keys()]
    file_contents = list(docs.values())

    # Create an AI context
    ai_context.set_input("file_names", file_names)
    ai_context.set_input("file_contents", file_contents)

    # Prepare the parameters for the GitHubDocsWriter operator
    step = {
        "parameters": {
            "repo_name": repo_name,
            "docs_folder_name": docs_folder_name
        }
    }
    try:
        # Run the GitHubDocsWriter operator to add docs to the repo
        GitHubDocsWriter().run_step(branch,step, ai_context)

        print(f"Documentation added to {repo_name}/{docs_folder_name} successfully!")
        return "Ok"
    except Exception as e:
        return str(e)
    