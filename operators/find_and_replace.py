import json

from operators.util import parse_parameter_structures

from .base_operator import BaseOperator
from ai_context import AiContext


class FindAndReplace(BaseOperator):

    @staticmethod
    def declare_name():
        return 'Find And Replace'

    @staticmethod
    def declare_category():
        return BaseOperator.OperatorCategory.MANIPULATE_DATA.value
    
    @staticmethod
    def declare_icon():
        return "switch.png"
    
    @staticmethod
    def declare_allow_batch():
        return True
    
    @staticmethod
    def declare_inputs():
        return [
            {
                "name": "input",
                "data_type": "string",
            }
        ]

    @staticmethod
    def declare_parameters():
        return [
            {
                "name": "replacements",
                "data_type": "object[]",
                "structure": [
                    {
                        "name": "find_word",
                        "data_type": "string",
                        "placeholder": "Word to find"
                    },
                    {
                        "name": "replace_with",
                        "data_type": "string",
                        "placeholder": "Word to replace it with"
                    }
                ]
            }
        ]

    @staticmethod
    def declare_outputs():
        return [
            {
                "name": "output_string",
                "data_type": "string",
            }
        ]

    def run_step(self, step, ai_context: AiContext):
        input_string = ai_context.get_input('input', self)
        replacements = step['parameters'].get('replacements')

        # Convert the input string to lowercase and remove commas and periods
        input_string = input_string.lower().replace(',', '').replace('.', '')

        # Split the input string into words
        words = input_string.split()

        # Using the parameter structure provided
        replacements_dict = parse_parameter_structures(replacements)

        # Iterate over each replacement object and replace words in the list
        for replacement in replacements_dict.values():
            find_word = replacement['find_word'].lower()
            replace_with = replacement['replace_with'].lower()

            # Replace the word in the list of words
            words = [replace_with if word == find_word else word for word in words]

        # Join the words back into a string
        output_string = ' '.join(words)

        ai_context.add_to_log(f"String from find and replace: {output_string}")
        ai_context.set_output('output_string', output_string, self)
        

