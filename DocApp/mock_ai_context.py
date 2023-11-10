from unittest.mock import Mock, patch
import tiktoken
import openai
import os

encoding = tiktoken.encoding_for_model("gpt-4")

class MockAiContext:
    def __init__(self):
        self.inputs = {}
        self.outputs = {}
        
        self.log = []

    def get_input(self, name, op_type):
        return self.inputs[name]

    def get_secret(self, env_var_name):
        try:
            return os.environ[env_var_name]
        except KeyError:
            print(f"get_secret: Environment variable '{env_var_name}' is not set.")
            return None

    def set_output(self, name, value, operator):
        # Store the output data
        self.outputs[name] = value

    def add_to_log(self, message, color=None, save=False):
        # Store the log message
        self.log.append(message)

    def run_chat_completion(self, msgs=None, prompt=None):
        
        openai.api_key = os.environ['AZURE_OPENAI_KEY']
        openai.api_type = "azure"
        openai.api_base = os.environ["AZURE_OPENAI_ENDPOINT"]
        openai.api_version = '2023-05-15'
        deployment_name = "reportes-msp"

        if not openai.api_key:
            raise ValueError("AZURE_OPENAI_KEY environment variable is not set.")

        max_tokens = 32000
        mn = 'gpt-4'
        temperature = 1.5
        tokens = encoding.encode(prompt, allowed_special="all")
        token_count = len(tokens)
        print(f"Token count: {token_count}")

        chat=[
            {"role": "system", "content": msgs},
            {"role": "user", "content": prompt},
        ]
        # print(chat)
        # if prompt is not None:
        #     msgs = [{"role": "user", "content": prompt}]
        # print(msgs)
        try:
            completion = openai.ChatCompletion.create(
                messages=chat,
                temperature=temperature,
                engine=deployment_name,
                max_tokens=max_tokens-token_count,
                n=1,
                stop=None,
            )
        except Exception as e:
            print(f"Exception: {e}")
            return str(e)
        print("hola")
        res = completion.choices[0].message.content
        return res
        
    # Methods below are not supposed to be used by operators.
    def set_input(self, name, value):
        self.inputs[name] = value  
        
    def get_output(self, name):
        return self.outputs.get(name)


