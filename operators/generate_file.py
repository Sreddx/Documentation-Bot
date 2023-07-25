from io import BytesIO
import re

from docx import Document

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

from ai_context import AiContext
from .base_operator import BaseOperator


class GenerateFile(BaseOperator):
    @staticmethod
    def declare_name():
        return 'Generate File'

    @staticmethod
    def declare_category():
        return BaseOperator.OperatorCategory.MANIPULATE_DATA.value

    @staticmethod
    def declare_description():
        return "Writes the content to a file given a string and returns a download link to the file. Supports .pdf and .docx filetypes"

    @staticmethod
    def declare_icon():
        return "file.png"

    @staticmethod
    def declare_allow_batch():
        return True

    @staticmethod
    def declare_parameters():
        return [
            {
                "name": "file_name",
                "data_type": "string",
                "placeholder": "Ex. 'letter'",
                "description": "The name of the file, no need to specify the extension here."
            },
            {
                "name": "file_type",
                "data_type": "enum(.pdf,.docx,.txt)",
                "description": "The type of the file to generate"
            }
        ]

    @staticmethod
    def declare_inputs():
        return [
            {
                "name": "file_contents",
                "data_type": "string",
                "placeholder": "Ex. The text of a letter that should be in a PDF",
                "optional": "1"
            }
        ]

    @staticmethod
    def declare_outputs():
        return [
            {
                "name": "generated_file_name",
                "data_type": "string",
            }
        ]

    def run_step(self, step, ai_context: AiContext):
        params = step['parameters']

        file_contents = ai_context.get_input('file_contents', self)

        file_name = params.get("file_name")
        file_type = params.get("file_type")

        file_name = file_name + file_type.strip()

        try:
            file_data = None
            if ".pdf" in file_type:
                file_data = self.get_pdf_bytestream(file_contents)
            elif ".docx" in file_type:
                file_data = self.get_docx_bytestream(file_contents)
            elif ".txt" in file_type:
                file_data = self.get_txt_bytestream(file_contents)

            generated_file_name = ai_context.store_file(file_data, file_name)

            ai_context.pl_run.memory_objects_written += [
                f'file:{generated_file_name}']
            ai_context.pl_run.save_mo_to_spanner()

            ai_context.set_output('generated_file_name',
                                  generated_file_name, self)
            ai_context.add_to_log(
                f"Successfully generated file {self.filter_run_id(generated_file_name)}!")
        except Exception as e:
            ai_context.add_to_log(f"Failed to generate error: {str(e)}")

    def get_docx_bytestream(self, file_contents):
        # Create and add text to new Document object
        document = Document()
        document.add_paragraph(file_contents)

        # Write Document object as byte stream
        document_bytes = BytesIO()
        document.save(document_bytes)
        document_bytes.seek(0)
        return document_bytes

    def get_pdf_bytestream(self, file_contents):
        # Create a file-like buffer to receive PDF data.
        pdf_bytes = BytesIO()

        # Create the PDF object, using the buffer as its "file."
        pdf = canvas.Canvas(pdf_bytes, pagesize=letter)

        textobject = pdf.beginText()
        textobject.setTextOrigin(inch, inch * 10)

        textobject.setFont("Times-Roman", 12)

        for line in self.get_pdf_lines(file_contents):
            textobject.textLine(line)

        pdf.drawText(textobject)
        pdf.showPage()
        pdf.save()

        pdf_bytes.seek(0)
        return pdf_bytes
    
    def get_txt_bytestream(self, file_contents):
        txt_bytes = BytesIO()
        txt_bytes.write(file_contents.encode('utf-8'))
        txt_bytes.seek(0)
        return txt_bytes

    def get_pdf_lines(self, raw_string):
        # Assuming 8.5" x 11" paper with 1-inch margins
        max_line_length = 95
        num_chars = len(raw_string)

        lines = []
        current_line = ""
        for i in range(num_chars):
            if raw_string[i] == '\n':
                # Newline character counts as end of line
                lines.append(current_line)
                current_line = ""
            else:
                current_line += raw_string[i]

                if len(current_line) >= max_line_length:
                    last_word_end = current_line.rfind(" ")

                    complete_line = current_line[:last_word_end]

                    lines.append(complete_line)

                    if last_word_end < len(current_line):
                        current_line = current_line[last_word_end + 1:]
                    else:
                        current_line = ""

        if current_line:
            lines.append(current_line)
        return lines

    def filter_run_id(self, file_name):
        # The regex pattern is any 22 characters followed by a slash at the start of the string
        # This should just filter out the run_id + "/"
        pattern = r"^.{22}/"

        # Remove run_id and return file_name
        return re.sub(pattern, "", file_name)
