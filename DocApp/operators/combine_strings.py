from .base_operator import BaseOperator
from ai_context import AiContext


class CombineStrings(BaseOperator):
    @staticmethod
    def declare_name():
        return 'CombineStrings'

    @staticmethod
    def declare_description():
        return 'This operator combines two input strings using a given format.'

    @staticmethod
    def declare_category():
        return BaseOperator.OperatorCategory.MANIPULATE_DATA.value

    @staticmethod
    def declare_icon():
        return "combine.png"

    @staticmethod
    def declare_parameters():
        return [
            {
                "name": "format",
                "data_type": "string",
                "placeholder": "Ex: 'This is input 1: {input1} This is input 2: {input2}'",
                "description": "The format string to combine the input strings. Use {input1} and {input2} as placeholders."
            }
        ]

    @staticmethod
    def declare_allow_batch():
        return True

    @staticmethod
    def declare_inputs():
        return [
            {
                "name": "input1",
                "data_type": "string",
                "placeholder": "Enter the first input string",
                "optional": "1",
                "description": "The first input string to be combined."
            },
            {
                "name": "input2",
                "data_type": "string",
                "placeholder": "Enter the second input string",
                "optional": "1",
                "description": "The second input string to be combined."
            }
        ]

    @staticmethod
    def declare_outputs():
        return [
            {
                "name": "combined_string",
                "data_type": "string",
                "description": "The combined string of input1 and input2, formatted according to the specified format string."
            }
        ]

    def run_step(
        self,
        step,
        ai_context: AiContext
    ):
        input1 = ai_context.get_input('input1', self) or ''
        input2 = ai_context.get_input('input2', self) or ''
        params = step['parameters']
        format_string = params.get('format')
        try:
            combined_string = format_string.format(
                input1=input1, input2=input2)
            ai_context.add_to_log(f"Successfully combined strings", log_level="VERBOSE")
            ai_context.set_output('combined_string', combined_string, self)

        except Exception as e:
            ai_context.add_to_log(
                f"Failed to combine strings. Error: {e}", color='red')