from operators.ask_chatgpt import AskChatGpt
from operators.github_file_read import GitHubFileReader
from operators.github_docs_writer import GitHubDocsWriter
from mock_ai_context import MockAiContext

def check_regex_with_repo(repo_info):
    # Create mock ai context
    test_ai_context = MockAiContext()
    

    # Get repo file names and contents into ai context
    GitHubFileReader().retrieve_github_files(repo_info, test_ai_context)
    print(test_ai_context.log)
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
            "question": """
                    Generar documentación en formato Markdown para el siguiente código. Esta documentación debe resumir el propósito y los detalles técnicos de este archivo de código.

                    Contexto del proyecto: El código y archivo proporcionado forma parte de un proyecto Flask siguiendo la metodología REST. El backend soporta la carga de archivos a AWS S3, preparando el sistema para analizar y procesar la información contenida en esos archivos, ya sean imágenes o videos.

                    Utilice encabezados para dividir la documentación en las siguientes secciones:

                    1. **Resumen**: Un resumen de maximo tres oraciones sobre la funcionalidad de este componente, tomando como base todo el codigo proporcionado correspondiente a este blueprint.
                    2. **Endpoints**: Describa brevemente cada endpoint y su propósito siguiendo la estructura:
                    - **Breve definición del endpoint y su función** (de una oración).
                    - **Método**: (GET, POST, etc.)
                    - **Ruta**: (/ruta/del/endpoint)
                    - **Propósito**: (Descripción breve del objetivo del endpoint)
                    - **Inputs**: (Parámetros esperados)
                    - **Ejemplo de Input**: (Ejemplo de los datos de entrada)
                    3. **Dependencias**: Describa brevemente las dependencias y su propósito.
                    4. **Funciones**: Breve resumen de las funciones presentes en el código.
                    5. **Solicitudes**: Si el código envía solicitudes a una API u otro sistema externo, describa la solicitud, incluidos los encabezados, los parámetros y la carga útil.
                    6. **Salidas**: Describa brevemente las salidas y su propósito.

                    Asegúrese de que la documentación sea clara, precisa y fácil de seguir. Si es necesario, consulte la documentación de Flask para obtener más información sobre cómo estructurar la documentación de un proyecto Flask RESTful.
                    Apeguese estrictamente a las indicacones proporcionadas en el contexto del proyecto, se asume que el lector de esta documentacion ya comprende que se trata de un backend webapp con flask y rest no es neceasario aclararlo dentro de la documentacion.
                    """,
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
        ai_context.set_input("question", prompt_info["parameters"]["question"] + "- El siguiente codigo es el contenido del archivo:" + ai_context.get_output("file_contents")[i])
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
            with open("TestDocs/" + file_name.replace("/", "_") + ".md", "w", encoding="utf-8") as f:
                f.write(file_content)
    except Exception as e:
        print("Error in saving documentation to TestDocs folder: " + str(e))
    return "docs generated successfully"


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
    