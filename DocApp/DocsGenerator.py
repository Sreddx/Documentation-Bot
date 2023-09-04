from operators.ask_chatgpt import AskChatGpt
import openai


prompt_info = {
    "parameters": {
        "question": "What is faster a lion or a ferrari?",
        "context": "",
        "function": ""
    },


}



response = AskChatGpt().run_step(prompt_info, ai_context=None)


print(response)
