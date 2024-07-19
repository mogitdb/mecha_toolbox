import fitz
import os
import sys
import subprocess
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QLineEdit, QMessageBox, QFileDialog, QProgressBar)
from PySide6.QtCore import Signal, QThread

class PDFScraperThread(QThread):
    update_progress = Signal(str)
    scraping_complete = Signal(str)
    scraping_failed = Signal(str)

    def __init__(self, pdf_path):
        super().__init__()
        self.pdf_path = pdf_path

    def run(self):
        try:
            documents_path = os.path.expanduser("~/Documents")
            output_folder = os.path.join(documents_path, "PDFScraper")
            img_subfolder = "img"
            img_output_folder = os.path.join(output_folder, img_subfolder)
            
            if not os.path.exists(img_output_folder):
                os.makedirs(img_output_folder)

            image_paths = self.convert_pdf_to_images(self.pdf_path, img_output_folder)
            self.create_markdown_file(image_paths, output_folder, img_subfolder)

            self.scraping_complete.emit(output_folder)
        except Exception as e:
            self.scraping_failed.emit(str(e))

    def convert_pdf_to_images(self, pdf_path, img_output_folder):
        pdf = fitz.open(pdf_path)
        image_paths = []
        for page_num in range(len(pdf)):
            page = pdf[page_num]
            zoom = 2
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            image_filename = f"slide_{page_num + 1}.png"
            image_path = os.path.join(img_output_folder, image_filename)
            pix.save(image_path)
            image_paths.append(image_path)
            self.update_progress.emit(f"Converted page {page_num + 1} to image")
        pdf.close()
        return image_paths

    def create_markdown_file(self, image_paths, output_folder, img_subfolder):
        md_filename = "slides.md"
        md_filepath = os.path.join(output_folder, md_filename)
        with open(md_filepath, 'w') as md_file:
            md_file.write('# Slides\n\n')
            for image_path in image_paths:
                image_filename = os.path.basename(image_path)
                md_file.write(f"![]({img_subfolder}/{image_filename})\n\n")
        self.update_progress.emit(f"Markdown file created: {md_filepath}")

class PDFScraperDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PDF Scraper")
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.file_label = QLabel("Select a PDF file to scrape:")
        layout.addWidget(self.file_label)

        file_layout = QHBoxLayout()
        self.file_entry = QLineEdit()
        file_layout.addWidget(self.file_entry)
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.select_file)
        file_layout.addWidget(self.browse_button)
        layout.addLayout(file_layout)

        self.scrape_button = QPushButton("Scrape PDF")
        self.scrape_button.clicked.connect(self.start_scraping)
        layout.addWidget(self.scrape_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("")
        layout.addWidget(self.progress_label)

        self.view_output_button = QPushButton("View Output Folder")
        self.view_output_button.clicked.connect(self.view_output_folder)
        self.view_output_button.setVisible(False)
        layout.addWidget(self.view_output_button)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf)")
        if file_path:
            self.file_entry.setText(file_path)

    def start_scraping(self):
        pdf_path = self.file_entry.text()
        if not pdf_path:
            QMessageBox.warning(self, "Error", "Please select a PDF file to scrape.")
            return

        self.scrape_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_label.setText("Starting PDF scraping...")

        self.scraper_thread = PDFScraperThread(pdf_path)
        self.scraper_thread.update_progress.connect(self.update_progress_label)
        self.scraper_thread.scraping_complete.connect(self.scraping_complete)
        self.scraper_thread.scraping_failed.connect(self.scraping_failed)
        self.scraper_thread.start()

    def update_progress_label(self, message):
        self.progress_label.setText(message)

    def scraping_complete(self, output_folder):
        self.progress_bar.setVisible(False)
        self.scrape_button.setEnabled(True)
        self.view_output_button.setVisible(True)
        self.progress_label.setText("PDF scraping complete")

        message = f"PDF scraped successfully!\nOutput folder: {output_folder}"
        QMessageBox.information(self, "Success", message)

    def scraping_failed(self, error_message):
        self.progress_bar.setVisible(False)
        self.scrape_button.setEnabled(True)
        self.progress_label.setText("PDF scraping failed")
        QMessageBox.critical(self, "Error", f"An error occurred: {error_message}")

    def view_output_folder(self):
        output_folder = os.path.expanduser("~/Documents/PDFScraper")
        if sys.platform == 'win32':
            os.startfile(output_folder)
        elif sys.platform == 'darwin':
            subprocess.run(['open', output_folder])
        else:
            subprocess.run(['xdg-open', output_folder])

def show_pdf_scraper_dialog(parent):
    dialog = PDFScraperDialog(parent)
    dialog.exec()