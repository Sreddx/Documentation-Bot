from flask import Flask, request, jsonify
import json
import DocsGenerator 
from mock_ai_context import MockAiContext
app = Flask(__name__)

@app.route("/")
def index():
    return "Hello, world!"



@app.route("/generate_docs", methods=['POST'])
def generate_docs_endpoint():
    ai_context = MockAiContext()
    data = request.json

    repo_name = data.get('repo_name', "") # iNBest-cloud/Telematica_AI_0723
    folders = data.get('folders', "") # src
    file_regex = data.get('file_regex', "") #.*.tsx
    branch = data.get('branch', "") # develop
    folders = folders.replace(" ", "").split(',')
    context=""
    repo_info = {
        "parameters": {
            "repo_name": repo_name,
            "folders": folders,
            "file_regex": file_regex,
            "branch": branch
        },
    }


    try:
        docs = DocsGenerator.generate_docs(ai_context,context,repo_name, folders, file_regex, branch)
        return jsonify(docs)
    except ValueError as e:
        print(str(e))
        return jsonify({"error": str(e)}), 400  # 400 is HTTP status code for Bad Request
    
@app.route("/check_regex_with_repo", methods=['POST'])
def check_regex_with_repo_endpoint():
    data = request.json
    repo_name = data.get('repo_name')
    folders = data.get('folders').split(',')
    file_regex = data.get('file_regex')
    branch = data.get('branch')
    repo_info = {

        "repo_name": repo_name,
        "folders": folders,
        "file_regex": file_regex,
        "branch": branch

    }
    
    # Make sure all necessary parameters are provided
    if not repo_name or not folders or not file_regex or not branch:
        return jsonify({"error": "All parameters must be provided!"}), 400  # Bad Request

    try:
        # Call the function and get the result
        file_names = DocsGenerator.check_regex_with_repo(repo_info)
        
        return jsonify({f"Checked regex:{file_regex} for files from repo {repo_name} in branch {branch}:": file_names})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route("/add_docs_to_repo", methods=['POST'])
def add_docs_to_repo_endpoint():
    try:
        data = request.json

        context = data.get('context')
        repo_name = data.get('repo_name')
        folders = data.get('folders').replace(" ", "").split(',')
        file_regex = data.get('file_regex')
        branch = data.get('branch')
        docs_folder_name = data.get('docs_folder_name')
        
        # Ensure all required parameters are provided
        if not context or not repo_name or not folders or not file_regex or not branch or not docs_folder_name:
            return jsonify({"error": "All parameters must be provided!"}), 400  # Bad Request

        result = DocsGenerator.add_docs_to_repo(context, repo_name, folders, file_regex, branch, docs_folder_name)

        if result == "Ok":
            return jsonify({"message": "Documentation added successfully!"}), 200
        else:
            return jsonify({"error": result}), 500  # Internal Server Error

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()