import json

from .base_operator import BaseOperator
from ai_context import AiContext


class WriteJsonValue(BaseOperator):
    @staticmethod
    def declare_name():
        return 'WriteJsonValue'

    @staticmethod
    def declare_category():
        return BaseOperator.OperatorCategory.MANIPULATE_DATA.value

    @staticmethod
    def declare_description():
        return "Writes a value to a JSON object given a JSON string, key, and value"

    @staticmethod
    def declare_parameters():
        return [
            {
                "name": "key",
                "data_type": "string",
                "placeholder": "Ex: 'name'"
            }
        ]

    @staticmethod
    def declare_allow_batch():
        return True

    @staticmethod
    def declare_inputs():
        return [
            {
                "name": "json_string",
                "data_type": "string",
                "description": "Stringified JSON that you want to add a value to"
            },
            {
                "name": "json_value",
                "data_type": "any",
                "description": "This can a string representing a json object, a json array, or a string"
            }
        ]

    @staticmethod
    def declare_outputs():
        return [
            {
                "name": "updated_json_string",
                "data_type": "string",
            }
        ]

    def add_or_update_key(self, json_object, key, json_value):
        try:
            value = json.loads(json_value)
        except Exception as e:
            value = json_value

        json_object[key] = value

        return json_object

    def run_step(
        self,
        step,
        ai_context: AiContext
    ):
        json_string = ai_context.get_input('json_string', self)
        json_value = ai_context.get_input('json_value', self)

        params = step['parameters']
        key = params.get('key')

        try:
            json_object = json.loads(json_string)

            updated_json_object = self.add_or_update_key(
                json_object, key, json_value)
            updated_json_string = json.dumps(updated_json_object)

            ai_context.add_to_log(
                f"Updated JSON string: {updated_json_string}")
            ai_context.set_output('updated_json_string',
                                  updated_json_string, self)

        except Exception as e:
            ai_context.add_to_log(
                f"Failed to write JSON values. Error: {e}", color='red')
