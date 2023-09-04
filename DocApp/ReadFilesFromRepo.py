from operators.github_file_read import GitHubFileReader 
from mock_ai_context import MockAiContext
import os


# Set dictionary for repo_info
repo_info = {
    "parameters": {
        "repo_name": "iNBest-cloud/Telematica_AI_0723",
        "folders": "src",
        "file_regex": ".*.tsx",
        "branch": "develop"
    },
}

test_ai_context = MockAiContext()




# We will test the github file reader operator here with the corresponding credentials before creating an endpoint for it


GitHubFileReader().run_step(repo_info,test_ai_context)
print(test_ai_context.get_output("file_names"))







