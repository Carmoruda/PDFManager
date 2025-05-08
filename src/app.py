import os
import sys
from zipfile import ZipFile

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (QApplication, QCheckBox, QFileDialog, QHBoxLayout,
                             QLabel, QLineEdit, QMessageBox, QProgressDialog,
                             QPushButton, QSpinBox, QSystemTrayIcon,
                             QVBoxLayout, QWidget)

from splitter import PDFSplitter


class MainWindow(QWidget):
    """Main application window for the PDf Splitter.

    This class initializes the user interface for the PDF Splitter application,
    allowing users to select a PDF file, specify options, and generate an executable.

    Arguments:
            QWidget:  The base class for the MainWindow, providing the core functionality
                      for creating and managing the window and its components.


    Attributes:
        splitter (PDFSplitter): Instance of the PDFSplitter class that handles
                                the logic for splitting PDFs.

    """

    def __init__(self):
        super().__init__()

        icon_path = self.resource_path("icons/arrows.ico")
        self.icon = QIcon(icon_path)
        self.SystemTray = QSystemTrayIcon(self.icon)
        self.SystemTray.setIcon(self.icon)
        self.SystemTray.setVisible(True)

        self.splitter = PDFSplitter()
        self.splitter.progress_signal.connect(self.update_progress)

        self.initUI()

    def initUI(self):
        """Set up the user interface components and layout.

        Creates the layout and initializes the widgets for the main window,
        including input fields for selecting PDF files, options for splitting, and buttons
        to perform actions such as splitting the PDF and clearing fields.
        """
        self.setWindowTitle("PDF Splitter")
        self.setWindowIcon(self.icon)
        self.setFixedSize(QSize(400, 200))

        # Create main layout that holds all widgets
        main_layout = QVBoxLayout()
        pdf_input_layout = QHBoxLayout()
        pdf_output_layout = QHBoxLayout()
        pages_layout = QHBoxLayout()

        # Input field for the PDF
        self.script_input = QLineEdit(self)
        self.script_input.setPlaceholderText("Select your PDF file")
        pdf_input_layout.addWidget(self.script_input)

        # Button to open file dialog for PDF selection
        self.browse_button = QPushButton("Browse...", self)
        self.browse_button.clicked.connect(self.openFileDialog)
        pdf_input_layout.addWidget(self.browse_button)

        # Add PDF Layout to main layout
        main_layout.addLayout(pdf_input_layout)

        # Input field for the output directory
        self.output_directory = QLineEdit(self)
        self.output_directory.setPlaceholderText("Select output directory")
        pdf_output_layout.addWidget(self.output_directory)

        # Button to open file dialog for directory selection
        self.browse_output_button = QPushButton("Browse...", self)
        self.browse_output_button.clicked.connect(self.openDirectoryDialog)
        pdf_output_layout.addWidget(self.browse_output_button)

        # Add PDF Layout to main layout
        main_layout.addLayout(pdf_output_layout)

        # Input for the number of pages that each PDf will have.
        self.pages_num_label = QLabel("Number of pages per PDF:")
        self.pages_num_label.setMaximumWidth(145)
        pages_layout.addWidget(self.pages_num_label)

        self.pages_num = QSpinBox()
        self.pages_num.setMinimum(1)
        self.pages_num.setSingleStep(1)
        self.pages_num.valueChanged.connect(self.ValueChangePages)
        pages_layout.addWidget(self.pages_num)

        # Add number of pages Layout to main Layout
        main_layout.addLayout(pages_layout)

        # Checkbox to compress to .zip
        self.compres_zip_checkBox = QCheckBox("Compress PDFs to .zip", self)
        main_layout.addWidget(self.compres_zip_checkBox)

        # Buttons to split the pdf
        button_layout = QHBoxLayout()
        split_button = QPushButton("Split PDF", self)
        split_button.clicked.connect(self.splitPDF)
        button_layout.addWidget(split_button)

        clear_button = QPushButton("Clear fields", self)
        clear_button.clicked.connect(self.clearFields)
        button_layout.addWidget(clear_button)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def openFileDialog(self):
        """Open a file dialog to select a PDF file.

        Allow the user to browse their file system and select a PDF file.
        The selected file path is then set to the input field.
        """

        file_name = QFileDialog.getOpenFileName(
            self,
            "Select your PDF File",
            os.path.expanduser("~"),
            "PDF Files (*.pdf);;All Files (*)",
        )

        if file_name:
            self.script_input.setText(file_name[0])

        self.splitter.input_pdf_path = file_name[0]

    def openDirectoryDialog(self):
        """Open a directory dialog to select an output directory.

        Allows the user to select a directory where the split PDFs will be saved.
        The selected directory path is then set to the input field.
        """

        directory_name = QFileDialog.getExistingDirectory(
            self, "Select directory", os.path.expanduser("~")
        )

        if directory_name:
            self.output_directory.setText(directory_name)

        self.splitter.output_directory_path = directory_name

    def ValueChangePages(self, pages_num):
        """Update the number of pages per PDF.

        This method is called when the value in the pages spin box is changed.
        It updates the pages_per_pdf attribute with the new value.

        Arguments:
                pages_num (int): The new number of pages per PDF.
        """
        self.splitter.pages_per_pdf = pages_num

    def splitPDF(self):
        """Trigger the PDF splitting process.

        Called when the user clicks the "Split PDF" button.
        It retrieves the current settings and starts the splitting operation.
        The output will be optionally compressed into a ZIP file based on user selection.
        """

        # Check if the selected file is a PDF (if not, return and send error message)
        if not self.splitter.check_pdf(self.splitter.input_pdf_path):
            button = QMessageBox.critical(
                self,
                "Error!",
                "The selected file is not a pdf.",
                buttons=QMessageBox.StandardButton.Ok,
                defaultButton=QMessageBox.StandardButton.Ok,
            )
            return

        # If the pdf and directory exist process and split
        if os.path.isfile(self.splitter.input_pdf_path) and os.path.isdir(
            self.splitter.output_directory_path
        ):
            self.splitter.compress_zip = self.compres_zip_checkBox.isChecked()

            self.progress_bar = QProgressDialog(
                "Splitting PDF...", "Cancel", 0, 100, self
            )
            self.progress_bar.setModal(True)
            self.progress_bar.setValue(1)
            self.progress_bar.setWindowTitle("PDF Splitter")
            self.progress_bar.show()
            self.splitter.split_pdf()

            if self.compres_zip_checkBox.isChecked():
                self.zip_pdf()

            button = QMessageBox.information(
                self,
                "PDF Splitter",
                "Pdfs have been split successfully!",
                buttons=QMessageBox.StandardButton.Ok,
                defaultButton=QMessageBox.StandardButton.Ok,
            )

        # If there is no
        elif not self.script_input.text():
            button = QMessageBox.critical(
                self,
                "Error!",
                "No file selected.",
                buttons=QMessageBox.StandardButton.Ok,
                defaultButton=QMessageBox.StandardButton.Ok,
            )
        elif not self.output_directory.text():
            button = QMessageBox.critical(
                self,
                "Error!",
                "No output directory selected.",
                buttons=QMessageBox.StandardButton.Ok,
                defaultButton=QMessageBox.StandardButton.Ok,
            )
        elif not os.path.isfile(self.splitter.input_pdf_path):
            button = QMessageBox.critical(
                self,
                "Error!",
                "The selected file doesn't exist.",
                buttons=QMessageBox.StandardButton.Ok,
                defaultButton=QMessageBox.StandardButton.Ok,
            )
        elif not os.path.isdir(self.splitter.output_directory_path):
            button = QMessageBox.critical(
                self,
                "Error!",
                "The selected output directory doesn't exist",
                buttons=QMessageBox.StandardButton.Ok,
                defaultButton=QMessageBox.StandardButton.Ok,
            )
        else:
            button = QMessageBox.critical(
                self,
                "Error!",
                "Unexpected error",
                buttons=QMessageBox.StandardButton.Ok,
                defaultButton=QMessageBox.StandardButton.Ok,
            )

    def clearFields(self):
        """Clear all input fields and reset settings.

        When the user clicks the "Clear fields" button, it resets the file
        path, number of pages per PDF, and compression option.
        """
        self.script_input.clear()
        self.output_directory.clear()
        self.pages_num.setValue(1)
        self.compres_zip_checkBox.setChecked(False)

        self.splitter.defaultAttributes()

    def update_progress(self, sender, **kwargs):
        """Update the progress bar of the splitting process.

        When the progress signal is emitted. It updates the
        progress bar's value based on the current progress.

        Args:
            sender: The object emitting the signal.
            kwargs: Additional arguments, including 'progress' indicating the progress.
        """
        progress = kwargs.get("progress", 0)
        self.progress_bar.setWindowTitle("PDF Splitter")
        self.progress_bar.setValue(progress)

        if self.progress_bar.wasCanceled():
            self.splitter.cancel_signal.send()

    def zip_pdf(self):
        """Compress the split PDFs into a ZIP file.

        Creates a ZIP file containing the split PDFs from the output
        directory, updating the progress bar during the compression process.
        """
        progress_dialog = QProgressDialog(
            "Compresing files into .zip...",
            "Cancel",
            1,
            self.splitter.sub_pdf_num,
            self,
        )
        progress_dialog.setModal(True)
        progress_dialog.setValue(1)
        progress_dialog.setWindowTitle("PDF Splitter")
        progress_dialog.show()

        progress_int = 0

        parent_directory = os.path.dirname(self.splitter.output_directory_path)
        print(parent_directory)
        file_name_no_extension = os.path.basename(self.splitter.input_pdf_path).split(
            "."
        )[0]

        with ZipFile(
            f"{parent_directory}/{os.path.basename(file_name_no_extension)}.zip", "w"
        ) as zip:
            for root, directories, files in os.walk(
                self.splitter.output_directory_path
            ):
                for file_name in files:
                    progress_dialog.setValue(progress_int)
                    file_path = os.path.join(root, file_name)
                    zip.write(file_path, arcname=file_name)
                    progress_int += 1

                    if progress_dialog.wasCanceled():
                        break

        progress_dialog.close()

    def resource_path(self, relative_path):
        """Obtiene la ruta absoluta a un recurso."""
        try:
            base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
