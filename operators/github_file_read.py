import json
import re

from github import Github

from .base_operator import BaseOperator

from ai_context import AiContext


class GitHubFileReader(BaseOperator):
    @staticmethod
    def declare_name():
        return 'Read files from GitHub'

    @staticmethod
    def declare_category():
        return BaseOperator.OperatorCategory.CONSUME_DATA.value

    @staticmethod
    def declare_icon():
        return "github.png"

    @staticmethod
    def declare_parameters():
        return [
            {
                "name": "repo_name",
                "data_type": "string",
                "placeholder": "user_name/repository_name"
            },
            {
                "name": "folders",
                "data_type": "string",
                "placeholder": "Enter the file paths, separated by commas",
                "input_format": "commaSeparatedList"
            },
            {
                "name": "file_regex",
                "data_type": "string",
                "placeholder": "Enter the regex to filter file names (e.g. '.*\.py' )"
            },
            {
                "name": "branch",
                "data_type": "string",
                "placeholder": "Enter the branch (default is main)"
            }
        ]

    @staticmethod
    def declare_inputs():
        return []

    @staticmethod
    def declare_inputs():
        return [
            {
                "name": "repo_name",
                "data_type": "string",
                "optional": "1"
            },
            {
                "name": "folders",
                "data_type": "string",
                "optional": "1"
            },
            {
                "name": "file_regex",
                "data_type": "string",
                "optional": "1"
            },
            {
                "name": "branch",
                "data_type": "string",
                "optional": "1"
            }
        ]

    @staticmethod
    def declare_outputs():
        return [
            {
                "name": "file_names",
                "data_type": "string[]",
            },
            {
                "name": "file_contents",
                "data_type": "string[]",
            }
        ]

    def run_step(self, step, ai_context: AiContext):
        params = step['parameters']
        
        # Fetch parameters or inputs as necessary
        repo_name = params.get('repo_name') or ai_context.get_input('repo_name', self)
        folders = params.get('folders') or ai_context.get_input('folders', self)
        file_regex = params.get('file_regex') or ai_context.get_input('file_regex', self)
        branch = params.get('branch', 'master') or ai_context.get_input('branch', self)

        folders = folders.replace(" ", "").split(',')

        self.read_github_files(repo_name, folders, file_regex, branch, ai_context)

    def read_github_files(self, repo_name, folders, file_regex, branch, ai_context):
        g = Github(ai_context.get_secret('github_access_token'))
        repo = g.get_repo(repo_name)

        file_names = []
        file_contents = []

        def file_matches_regex(file_path, file_regex):
            if not file_regex:
                return True

            return re.fullmatch(file_regex, file_path)

        def bfs_fetch_files(folder_path):
            queue = [folder_path]

            while queue:
                current_folder = queue.pop(0)

                contents = repo.get_contents(current_folder, ref=branch)

                for item in contents:
                    if item.type == "file" and file_matches_regex(item.path, file_regex):
                        file_content = item.decoded_content.decode('utf-8')
                        file_names.append(item.path)
                        file_contents.append(file_content)

                    elif item.type == "dir":
                        queue.append(item.path)

        for folder_path in folders:
            bfs_fetch_files(folder_path)

        ai_context.add_to_log(
            f"{self.declare_name()} Fetched {len(file_names)} files from GitHub repo {repo_name}:\n\r{file_names}", color='blue', save=True)

        ai_context.set_output('file_names', file_names, self)
        ai_context.set_output('file_contents', file_contents, self)
        return True
    