from operators.ask_chatgpt import AskChatGpt
from operators.github_file_read import GitHubFileReader
from mock_ai_context import MockAiContext
import openai

# Create dictionary for repo_info
repo_info = {
    "parameters": {
        "repo_name": "iNBest-cloud/Telematica_AI_0723",
        "folders": "src",
        "file_regex": ".*.tsx",
        "branch": "develop"
    },
}

# Create dictionary for prompt info
prompt_info = {
    "parameters": {
        "question": "Generate Markdown documentation for this code. This documentation is meant to summarize the purpose and technical details of this code file.Use headings to breakdown the documentation into the following sections: Summary: A one sentence summary of this component's functionality. Inputs: briefly describe the inputs and their purpose. Dependencies: briefly describe dependencies and their purpose. Outputs: briefly describe outputs and their purpose.",
        "context": "",
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
    test_ai_context.set_input("context", "The path of this file is the following and you can infer the name of the component from it:" + test_ai_context.get_output("file_contents")[i])
    test_ai_context.set_input("question", prompt_info["parameters"]["question"] + "-File Content:" + test_ai_context.get_output("file_contents")[i])
    try:
        AskChatGpt().run_step(prompt_info, ai_context=test_ai_context)
        docs[test_ai_context.get_output("file_names")[i]] = test_ai_context.get_output("chatgpt_response")
    except Exception as e:
        print("Error in generating documentation for file: " + test_ai_context.get_output("file_names")[i])
        print(str(e))
        continue

print(docs["src/App.tsx"])

# Save the documentation in TestDocs folder
for file_name, file_content in docs.items():
    with open("TestDocs/" + file_name.replace("/", "_") + ".txt", "w") as f:
        f.write(file_content)
