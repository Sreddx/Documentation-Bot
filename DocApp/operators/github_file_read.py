import json
import re
from dotenv import load_dotenv
import os
from github import Github
import traceback

from .base_operator import BaseOperator

from ai_context import AiContext

load_dotenv()

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


    def run_step(
        self, 
        step, 
        ai_context : AiContext
    ):
        params = step['parameters']
        print("hola")
        self.read_github_files(params, ai_context)
            
    
    def retrieve_github_files(self, params, ai_context : AiContext):
        repo_name = params['repo_name']
        folders = params.get('folders', [])
        file_regex = params.get('file_regex')
        branch = params.get('branch', 'main')
        specific_files = params.get('specific_files')

        print(f"Checking regex:{file_regex} for files from repo {repo_name} in branch {branch}...")
        print(f"Folders: {folders}")
        print(f"Specific files: {specific_files}")

        g = Github(ai_context.get_secret('GITHUB_ACCESS_TOKEN'))
        repo = g.get_repo(repo_name)

        matching_files = []

        def file_matches_regex(file_path, file_regex):
            if not file_regex:
                return True
            return re.fullmatch(file_regex, file_path)

        def bfs_check_files(folder_path):
            queue = [folder_path]

            while queue:
                current_folder = queue.pop(0)
                try:
                    contents = repo.get_contents(current_folder, ref=branch)  # Updated method name
                    for item in contents:
                        if item.type == "file" and file_matches_regex(item.path, file_regex):
                            matching_files.append(item.path)
                        elif item.type == "dir":
                            queue.append(item.path)
                except Exception as e:
                    ai_context.add_to_log(f"Error fetching content for {current_folder}: {str(e)}", color='red', save=True)
                    continue

        if specific_files:
            matching_files.extend(specific_files)
        else:
            for folder_path in folders:
                print(f"Checking folder: {folder_path}")
                bfs_check_files(folder_path)

        ai_context.add_to_log(f"Fetched {len(matching_files)} files from GitHub repo {repo_name}:\n\r{matching_files}", color='blue', save=True)
        ai_context.set_output('matching_files', matching_files, self)
        return True


    def read_github_files(self, params, ai_context):
        repo_name = params['repo_name']
        folders = params.get('folders', [])
        file_regex = params.get('file_regex')
        branch = params.get('branch', 'main')
        specific_files = params.get('specific_files')

        print(f"Reading files from repo {repo_name} in branch {branch}...")
        g = Github(ai_context.get_secret('GITHUB_ACCESS_TOKEN'))
        try:
            repo = g.get_repo(repo_name)
            print(repo)
        except Exception as e:
            print("Error in getting repo: " + str(e))
            print(traceback.format_exc())
            raise e
        
        file_names = []
        file_contents = []

        def file_matches_regex(file_path, file_regex):
            if not file_regex:
                return True
            return re.fullmatch(file_regex, file_path)

        def fetch_file_content(file_path):
            try:
                file_content = repo.get_contents(file_path, ref=branch).decoded_content.decode('utf-8')
                file_names.append(file_path)
                file_contents.append(file_content)
            except Exception as e:
                print(f"Error in fetching file content for {file_path}: " + str(e))
                print(traceback.format_exc())

        def bfs_fetch_files(folder_path):
            queue = [folder_path]

            while queue:
                current_folder = queue.pop(0)
                
                try:
                    contents = repo.get_contents(current_folder, ref=branch)
                except Exception as e:
                    print(f"Error in getting contents of {current_folder}: " + str(e))
                    print(traceback.format_exc())
                    continue

                for item in contents:
                    print(f"Processing {item.path}")
                    try:
                        if item.type == "file" and file_matches_regex(item.path, file_regex):
                            fetch_file_content(item.path)
                        elif item.type == "dir":
                            queue.append(item.path)
                    except Exception as e:
                        print(f"Error in processing {item.path}: " + str(e))
                        print(traceback.format_exc())
                        continue

        if specific_files:
            for file_path in specific_files:
                fetch_file_content(file_path)
        else:
            for folder_path in folders:
                bfs_fetch_files(folder_path)

        ai_context.add_to_log(f"{self.declare_name()} Fetched {len(file_names)} files from GitHub repo {repo_name}:\n\r{file_names}", color='blue', save=True)

        ai_context.set_output('file_names', file_names, self)
        ai_context.set_output('file_contents', file_contents, self)
        return True