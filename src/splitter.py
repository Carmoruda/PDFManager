import PyPDF2
import PyPDF2.errors
from blinker import Signal


class PDFSplitter:
    """Class for splitting PDF files into smaller parts.

    Provides functionalities to read a PDF file, split it into smaller
    PDFs based on a specified number of pages per document, and manage the progress
    of the splitting operation.

    Attributes:
        input_pdf_path (str): Path to the input PDF file to be split.
        output_directory_path (str): Directory where the split PDFs will be saved.
        pages_per_pdf (int): Number of pages each split PDF should contain.
        compress_zip (bool): Flag indicating whether to compress the output PDFs into a ZIP file.
        sub_pdf_num (int): Counter for the number of split PDFs generated.
        cancel (bool): Flag to indicate if the splitting process should be canceled.
        progress_signal (Signal): Signal emitted to indicate progress during the splitting process.
        cancel_signal (Signal): Signal emitted to request cancellation of the splitting process.
    """

    def __init__(self):
        self.defaultAttributes()
        self.progress_signal = Signal()
        self.cancel_signal = Signal()
        self.cancel_signal.connect(self.cancel_progress)

    def defaultAttributes(self):
        """Resets the attributes to their default values.

        Sets the initial values for the input PDF path, output directory path,
        pages per PDF, compression option, and counters.
        """
        self.input_pdf_path = ""
        self.output_directory_path = ""
        self.pages_per_pdf = 1
        self.compress_zip = False
        self.sub_pdf_num = 0
        self.cancel = False

    def check_pdf(self, pdf):
        try:
            read_pdf = PyPDF2.PdfReader(pdf)
            return True
        except PyPDF2.errors.PdfReadError:
            return False

    def read_pdf(self, pdf):
        """Reads a PDF file and returns a PdfReader object.

        Args:
            pdf (str): Path to the PDF file to be read.

        Returns:
            PdfReader: A PdfReader object representing the PDF file.
        """
        return PyPDF2.PdfReader(pdf)

    def split_pdf(self):
        """Splits the input PDF into smaller PDFs based on the specified number of pages.

        Reads the input PDF, creates new PDFs with the specified number of pages,
        and saves them to the output directory. Progress is reported via the progress_signal.
        If cancellation is requested, the process will stop.
        """
        # Open the pdf
        with open(self.input_pdf_path, "rb") as input_file:
            reader = self.read_pdf(input_file)
            total_pages = len(reader.pages)
            self.sub_pdf_num = 1

            for start_page in range(0, total_pages, self.pages_per_pdf):
                # New PDF Document
                writer = PyPDF2.PdfWriter()

                # Add the pages to the new PDF
                for page_num in range(
                    start_page, min(start_page + self.pages_per_pdf, total_pages)
                ):
                    writer.add_page(reader.pages[page_num])

                # Save the new pdf
                output_pdf_path = f"{self.output_directory_path}/{self.sub_pdf_num}.pdf"
                self.sub_pdf_num += 1

                with open(output_pdf_path, "wb") as output_file:
                    writer.write(output_file)

                progress = (start_page + self.pages_per_pdf) / total_pages * 100
                self.progress_signal.send(progress=int(progress))

                if self.cancel:
                    break

    def cancel_progress(self, sender, **kwargs):
        """Cancels the PDF splitting process.

        Sets the cancel flag to True, which will stop the splitting process
        if it is currently running.
        """
        self.cancel = True
