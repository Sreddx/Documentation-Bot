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
    def declare_icon():
        return "json.png"

    @staticmethod
    def declare_parameters():
        return [
            {
                "name": "key",
                "data_type": "string",
                "placeholder": "Ex: 'name'",
                "description": "The key in the JSON object where the value will be added or updated"
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
                "description": "This can be a string representing a JSON object, a JSON array, or a string"
            }
        ]

    @staticmethod
    def declare_outputs():
        return [
            {
                "name": "updated_json_string",
                "data_type": "string",
                "description": "The updated stringified JSON"
            }
        ]

    def parse_json_value(self, json_value):
        # If the passed value is a string, attempt to parse it as JSON
        if isinstance(json_value, str):
            try:
                parsed_value = json.loads(json_value)
                return self.parse_json_value(parsed_value)  # Recurse with the parsed value
            except Exception as e:
                return json_value  # If parsing fails, return the original string

        # If the passed value is a list, recurse into its elements
        elif isinstance(json_value, list):
            return [self.parse_json_value(item) for item in json_value]

        # If the passed value is a dictionary, recurse into its values
        elif isinstance(json_value, dict):
            return {key: self.parse_json_value(val) for key, val in json_value.items()}

        # For any other type, return the value as is
        else:
            return json_value

    def add_or_update_key(self, json_object, key, json_value):
        value = self.parse_json_value(json_value)
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
                f"Updated JSON string: {updated_json_string}", log_level="VERBOSE")
            ai_context.set_output('updated_json_string',
                                  updated_json_string, self)

        except Exception as e:
            ai_context.add_to_log(
                f"Failed to write JSON values. Error: {e}", color='red')