import json

from .base_operator import BaseOperator
from ai_context import AiContext


class ReadJsonValues(BaseOperator):
    @staticmethod
    def declare_name():
        return 'ReadJsonValues'

    @staticmethod
    def declare_category():
        return BaseOperator.OperatorCategory.MANIPULATE_DATA.value

    @staticmethod
    def declare_parameters():
        return [
            {
                "name": "keys",
                "data_type": "string",
                "placeholder": "Ex: 'key1,key2,key3'"
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
                "placeholder": "Enter the JSON string"
            }
        ]

    @staticmethod
    def declare_outputs():
        return [
            {
                "name": "json_values",
                "data_type": "string",
            }
        ]

    def get_values_from_keys(self, json_object, keys):
        """
        Function to retrieve values from JSON object using provided keys.
        Keys can include nested keys, separated by '.'. 
        The retrieved value is converted to a string if not already.
        """
        values = []

        for key in keys:
            temp_json_object = json_object
            nested_keys = key.split('.')

            for nested_key in nested_keys:
                if nested_key in temp_json_object:
                    temp_json_object = temp_json_object[nested_key]
                else:
                    # Break the loop if the key doesn't exist in the JSON object
                    break
            else:
                # Only executed if the loop didn't encounter a 'break'

                # Check if the result is a list or dict, and use json.dumps
                if isinstance(temp_json_object, (list, dict)):
                    values.append(json.dumps(temp_json_object))
                else:
                    # Convert to string if the result isn't a string
                    values.append(str(temp_json_object) if not isinstance(
                        temp_json_object, str) else temp_json_object)

        return values

    def run_step(
        self,
        step,
        ai_context: AiContext
    ):
        json_string = ai_context.get_input('json_string', self)

        params = step['parameters']
        keys = params.get('keys').split(',')

        try:
            json_object = json.loads(json_string)

            values = self.get_values_from_keys(json_object, keys)

            json_values = ', '.join(values)

            ai_context.add_to_log(f"Json values read: {json_values}")
            ai_context.set_output('json_values', json_values, self)

        except Exception as e:
            ai_context.add_to_log(
                f"Failed to read JSON values. Error: {e}", color='red')
