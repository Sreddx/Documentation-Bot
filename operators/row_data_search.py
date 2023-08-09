import spacy
from collections import deque
import heapq

from .base_operator import BaseOperator
from .util import strip_accents

nlp = spacy.load("en_core_web_sm")


class RowDataSearch(BaseOperator):
    @staticmethod
    def declare_name():
        return 'Row Data Search'

    @staticmethod
    def declare_description():
        return """Scan input text line by line and return up to 'nresults' 
               lines that are most relevant to the 'query' input/parameter."""

    @staticmethod
    def declare_icon():
        return "insert.png"

    @staticmethod
    def declare_allow_batch():
        return True

    @staticmethod
    def declare_category():
        return BaseOperator.OperatorCategory.MANIPULATE_DATA.value

    @staticmethod
    def declare_parameters():
        return [
            {
                "name": "nresults",
                "data_type": "integer",
                "placeholder": "Enter maximum number of search results. Default is 5."
            },
            {
                "name": "query",
                "data_type": "string",
                "placeholder": "Enter your query"
            }
        ]

    @staticmethod
    def declare_inputs():
        return [
            {
                "name": "text",
                "data_type": "string",
            },
            {
                "name": "query",
                "data_type": "string",
                "optional": "1"
            },
        ]

    @staticmethod
    def declare_outputs():
        return [
            {
                "name": "search_result",
                "data_type": "string",
            }
        ]

    def run_step(self, step, ai_context):
        p = step['parameters']

        text = ai_context.get_input('text', self)
        if text:
            text = self.prepare_text_for_search(text)
        else:
            ai_context.add_to_log("Input 'text' is None.")
            ai_context.set_output('search_result', '', self)
            return

        query = ai_context.get_input('query', self) or p['query']
        if query:
            query = self.prepare_text_for_search(query)
        else:
            ai_context.add_to_log("Query is None.")
            ai_context.set_output('search_result', '', self)
            return

        nresults = int(p.get('nresults') or 5)

        query_tokens = [token.text for token in nlp(
            query) if self.token_is_word(token)]

        lines = text.split('\n')

        results = []

        for line in lines:
            t = nlp(line)
            line_score = 0
            for token in t:
                for query_token in query_tokens:
                    line_score += self.token_match_score(query_token, token)

            if line_score > 0:  # Ensure non-zero score before adding to the results
                heapq.heappush(results, (-line_score, line))

        if not results:
            ai_context.add_to_log(
                'No matches found for the given query.', log_level="VERBOSE")
            ai_context.set_output('search_result', '', self)
            return

        top_results = [heapq.heappop(results)[1]
                       for _ in range(min(nresults, len(results)))]

        final_output = "\n".join(top_results)

        ai_context.add_to_log(
            f'Search result: {final_output}', log_level="VERBOSE")
        ai_context.set_output('search_result', final_output, self)

    def token_match_score(self, t1, t2):
        return 1.0 if str(t1).lower() == str(t2).lower() else 0

    def token_is_word(self, token):
        return not token.is_punct and not token.is_space and not token.is_stop

    def prepare_text_for_search(self, text):
        """Replaces commas in the text with spaces to make it suitable for search."""
        text = strip_accents(text)
        text = text.replace(',', ' ')
        text = text.lower()

        return text
