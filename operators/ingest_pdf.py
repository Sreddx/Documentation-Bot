import os
import io
import requests
import tempfile

from langchain.document_loaders import DirectoryLoader, PyMuPDFLoader
from google.cloud import storage
import tabula
import pandas as pd

from .base_operator import BaseOperator

from ai_context import AiContext


class IngestPDF(BaseOperator):
    @staticmethod
    def declare_name():
        return 'Ingest PDF'
    
    def declare_description():
        return 'Operator to take PDF and conert into blob of text. PDF can be an URI or a file that user uploaded to their workspace on AgentHub. Either option can be an input of parameter.'
    
    @staticmethod
    def declare_category():
        return BaseOperator.OperatorCategory.CONSUME_DATA.value
    
    @staticmethod
    def declare_allow_batch():
        return True

    @staticmethod
    def declare_parameters():
        return [
            {
                "name": "pdf_uri",
                "data_type": "string",
                "placeholder": "Enter the URL of the PDF"
            },
            {
                "name": "uploaded_file_name",
                "data_type": "string",
                "placeholder": "Enter the name.pdf of the uploaded PDF"
            }
            # TODO: uncomment when there are more than 1 methods of parsing PDF.
            #, 
            #{
            #    "name": "pdf_parsing_method",
            #    "data_type": "string",
            #    "placeholder": "default=tabula - for preservation of tables and spreadsheets"
            #}
        ]

    @staticmethod
    def declare_inputs():
        return [
            {
                "name": "pdf_uri",
                "data_type": "string",
                "optional": "1"
            },
            {
                "name": "uploaded_file_name",
                "data_type": "string",
                "optional": "1"
            }
        ]

    @staticmethod
    def declare_outputs():
        return [
            {
                "name": "pdf_content",
                "data_type": "string",
            }
        ]

    def run_step(
            self,
            step,
            ai_context: AiContext,
    ):
        params = step['parameters']
        pdf_uri = params.get('pdf_uri') or ai_context.get_input('pdf_uri', self)
        uploaded_file_name = params.get('uploaded_file_name') or ai_context.get_input('uploaded_file_name', self)
        self.ingest(pdf_uri, uploaded_file_name, ai_context)

    def ingest(self, pdf_uri, uploaded_file_name, ai_context):
        if uploaded_file_name:
            ai_context.add_to_log(f"Loading {uploaded_file_name} from storage.")
            file_data = self.load_pdf_from_storage(uploaded_file_name, False, ai_context)
            ai_context.add_to_log(f"Content from uploaded file {uploaded_file_name} has been scraped.")
            
        elif pdf_uri and self.is_url(pdf_uri):
            file_data = self.load_pdf_from_uri(pdf_uri)
            ai_context.add_to_log(f"Content from uri {pdf_uri} has been scraped.")
            
        else:
            ai_context.set_output('pdf_content', '', self)
            ai_context.add_to_log("No file to read.")
            return

        text = self.read_pdf(file_data)
        ai_context.set_output('pdf_content', text, self)
        

    def is_url(self, pdf_uri):
        # add url validation maybe?
        return True

    def load_pdf_from_uri(self, url):
        response = requests.get(url)
        response.raise_for_status()  # Ensure we got a valid response
        return response.content
    
    def load_pdf_from_storage(self, file_name, generated_this_run, ai_context):
        if generated_this_run:
            file_data = ai_context.get_file(file_name, ai_context.get_run_id())
        else:
            file_data = ai_context.get_file(file_name)
        return file_data
    
    def read_pdf(self, pdf):
        pd.set_option('display.max_colwidth', None)
        pdf_content = io.BytesIO(pdf)
        df_list = tabula.read_pdf(pdf_content, pages='all')
        pdf_content = "\n".join(df.to_string(index=False) for df in df_list)
        
        return pdf_content
    
        
