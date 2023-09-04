from operators.ask_chatgpt import AskChatGpt
from operators.github_file_read import GitHubFileReader
from mock_ai_context import MockAiContext

def check_regex_with_repo(repo_name, folders, file_regex, branch):
    # Create dictionary for repo_info
    repo_info = {
        "parameters": {
            "repo_name": repo_name,
            "folders": folders,
            "file_regex": file_regex,
            "branch": branch
        },
    }

    # Create mock ai context
    test_ai_context = MockAiContext()
    test_ai_context.set_input("context", "")

    # Get repo file names and contents into ai context
    GitHubFileReader().run_step(repo_info, test_ai_context)
    return test_ai_context.get_output("file_names")

    

    

def generate_docs(context,repo_name, folders, file_regex, branch):

    if not repo_name or not folders or not file_regex or not branch:
        raise ValueError("All parameters must have a non-empty value!")
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
            "question": "Generate Markdown documentation for this code. This documentation is meant to summarize the purpose and technical details of this code file.Use headings to breakdown the documentation into the following sections: Summary: A one sentence summary of this component's functionality. Inputs: briefly describe the inputs and their purpose. Dependencies: briefly describe dependencies and their purpose. Outputs: briefly describe outputs and their purpose.",
            "context": context,
            "function": ""
        },
    }

    # Create mock ai context
    test_ai_context = MockAiContext()
    test_ai_context.set_input("context", "")

    # Get repo file names and contents into ai context
    GitHubFileReader().run_step(repo_info, test_ai_context)
    print(test_ai_context.get_output("file_names"))

    num_files_to_read = len(test_ai_context.get_output("file_names"))
    docs = {}

    # Generate documentation for each file
    for i in range(num_files_to_read):
        test_ai_context.set_input("context", prompt_info["parameters"][context])
        test_ai_context.set_input("question", prompt_info["parameters"]["question"] + "-File Content:" + test_ai_context.get_output("file_contents")[i])
        try:
            AskChatGpt().run_step(prompt_info, ai_context=test_ai_context)
            docs[test_ai_context.get_output("file_names")[i]] = test_ai_context.get_output("chatgpt_response")
        except Exception as e:
            print("Error in generating documentation for file: " + test_ai_context.get_output("file_names")[i])
            print(str(e))
            continue
    
    # print(docs["src/App.tsx"]
    return docs

    # Save the documentation in TestDocs folder
    for file_name, file_content in docs.items():
        with open("TestDocs/" + file_name.replace("/", "_") + ".txt", "w") as f:
            f.write(file_content)
