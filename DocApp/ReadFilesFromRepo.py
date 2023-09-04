from operators.github_file_read import GitHubFileReader 

import os


# Set dictionary for repo_info
repo_info = {
    "parameters": {
        "repo_name": "iNBest-cloud/Telematica_AI_0723",
        "folders": "src",
        "file_regex": ".*(\.py|\.js)",
        "branch": "main"
    },
}
# Set variables for repo_info
repo_name = "iNBest-cloud/Telematica_AI_0723"
folders = repo_info["parameters"]["folders"].replace(" ", "").split(',')
file_regex = ".*.tsx"
branch = "develop"

# We will test the github file reader operator here with the corresponding credentials before creating an endpoint for it


# This function call is needed when calling the operator from the UI or in batches
# repo_doc = GitHubFileReader().run_step(repo_info)

# Direct call with the variables so that we can test the operator
file_names, file_contents = GitHubFileReader().read_github_files(repo_name, folders, file_regex, branch)



for file_name, file_content in zip(file_names, file_contents):
    print(f"File Name: {file_name}")
    print(f"File Content: {file_content}")
    print("\n\n")


