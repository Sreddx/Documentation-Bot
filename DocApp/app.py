from flask import Flask, request, jsonify
import json
import DocsGenerator 
app = Flask(__name__)

@app.route("/")
def index():
    return "Hello, world!"



@app.route("/generate_docs", methods=['POST'])
def generate_docs_endpoint():
    data = request.json

    repo_name = data.get('repo_name', "") # iNBest-cloud/Telematica_AI_0723
    folders = data.get('folders', "") # src
    file_regex = data.get('file_regex', "") #.*.tsx
    branch = data.get('branch', "") # develop

    try:
        docs = DocsGenerator.generate_docs(repo_name, folders, file_regex, branch)
        return jsonify(docs)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400  # 400 is HTTP status code for Bad Request
    
@app.route("/check_regex_with_repo", methods=['POST'])
def check_regex_with_repo_endpoint():
    data = request.json
    repo_name = data.get('repo_name')
    folders = data.get('folders')
    file_regex = data.get('file_regex')
    branch = data.get('branch')

    # Make sure all necessary parameters are provided
    if not repo_name or not folders or not file_regex or not branch:
        return jsonify({"error": "All parameters must be provided!"}), 400  # Bad Request

    # Call the function and get the result
    file_names = DocsGenerator.check_regex_with_repo(repo_name, folders, file_regex, branch)
    
    return jsonify({"file_names": file_names})


if __name__ == "__main__":
    app.run()