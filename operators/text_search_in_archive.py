import re

from .base_operator import BaseOperator

from ai_context import AiContext


class TextSearchInArchive(BaseOperator):
    @staticmethod
    def declare_name():
        return 'Text Search in Archive'

    @staticmethod
    def declare_category():
        return BaseOperator.OperatorCategory.DB.value

    @staticmethod
    def declare_icon():
        return "text_search.png"

    @staticmethod
    def declare_description():
        return "This operator allows you to search for text in an archive table."

    @staticmethod
    def declare_parameters():
        return [
            {
                "name": "query",
                "data_type": "string",
                "placeholder": "Query to search for (can be an input instead of parameter)",
                "description": "The text query to search for in the archive table."
            },
            {
                "name": "num_results",
                "data_type": "string",
                "placeholder": "Limit on number of results to return (optional, default=10)",
                "description": "The maximum number of search results to return."
            },
            {
                "name": "table_name",
                "data_type": "string",
                "placeholder": "Table name to search in",
                "description": "The name of the table in the archive to search in."
            },
            {
                "name": "visibility",
                "data_type": "enum(project,user,public)",
                "description": "The visibility of the search results: 'project', 'user', or 'public'."
            },
            {
                "name": "language",
                "data_type": "enum(english,simple,arabic,armenian,basque,catalan,danish,dutch,finnish,french,german,greek,hindi,hungarian,indonesian,irish,italian,lithuanian,nepali,norwegian,portuguese,romanian,russian,serbian,spanish,swedish,tamil,turkish,yiddish)",
                "description": "The language used for searching and analyzing the text."
            }
        ]

    @staticmethod
    def declare_inputs():
        return [
            {
                "name": "query",
                "data_type": "string",
                "optional": "1",
                "description": "The text query to search for in the archive table."
            }
        ]

    @staticmethod
    def declare_outputs():
        return [
            {
                "name": "search_results",
                "data_type": "string",
                "description": "The search results returned as a string."
            }
        ]

    def run_step(
        self,
        step,
        ai_context: AiContext
    ):
        p = step['parameters']
        query = ai_context.get_input('query', self) or p['query']

        r = ai_context.query_chunk_index(
            query,
            p.get('num_results', 10),
            p['table_name'],
            p['visibility'],
            p.get('language', 'english'),
        )

        ai_context.set_output('search_results', str(r), self)
        ai_context.add_to_log(f'Found: {r}')