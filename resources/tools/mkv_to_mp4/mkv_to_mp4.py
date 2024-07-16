import os
import sys
import subprocess
import shutil
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QFileDialog, QProgressBar, QMessageBox)
from PySide6.QtCore import Qt, Signal, QThread

class ConversionThread(QThread):
    update_progress = Signal(str)
    conversion_complete = Signal(str)

    def __init__(self, input_file, output_folder):
        super().__init__()
        self.input_file = input_file
        self.output_folder = output_folder

    def run(self):
        try:
            output_file = os.path.join(self.output_folder, os.path.splitext(os.path.basename(self.input_file))[0] + '.mp4')
            subprocess.run(['ffmpeg', '-i', self.input_file, '-codec', 'copy', output_file], check=True)
            self.conversion_complete.emit(output_file)
        except subprocess.CalledProcessError as e:
            self.update_progress.emit(f"An error occurred: {str(e)}")

class MkvToMp4Converter(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MKV to MP4 Converter")
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.select_button = QPushButton("Select MKV File")
        self.select_button.clicked.connect(self.select_file)
        layout.addWidget(self.select_button)

        self.progress_label = QLabel("Select an MKV file to convert")
        layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        button_layout = QHBoxLayout()
        self.convert_button = QPushButton("Convert")
        self.convert_button.clicked.connect(self.start_conversion)
        self.convert_button.setEnabled(False)
        button_layout.addWidget(self.convert_button)

        self.open_folder_button = QPushButton("Open Output Folder")
        self.open_folder_button.clicked.connect(self.open_output_folder)
        self.open_folder_button.setVisible(False)
        button_layout.addWidget(self.open_folder_button)

        layout.addLayout(button_layout)

        self.input_file = ""
        self.output_folder = os.path.expanduser("~/Desktop")

    def select_file(self):
        file_dialog = QFileDialog(self)
        self.input_file, _ = file_dialog.getOpenFileName(self, "Select MKV file", "", "MKV files (*.mkv)")
        if self.input_file:
            self.progress_label.setText(f"Selected file: {os.path.basename(self.input_file)}")
            self.convert_button.setEnabled(True)

    def start_conversion(self):
        if not self.check_dependencies():
            return

        self.conversion_thread = ConversionThread(self.input_file, self.output_folder)
        self.conversion_thread.update_progress.connect(self.update_progress_label)
        self.conversion_thread.conversion_complete.connect(self.conversion_finished)
        
        self.conversion_thread.start()
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.convert_button.setEnabled(False)
        self.select_button.setEnabled(False)

    def update_progress_label(self, message):
        self.progress_label.setText(message)

    def conversion_finished(self, output_file):
        self.progress_bar.setVisible(False)
        self.progress_label.setText(f"Conversion complete: {os.path.basename(output_file)}")
        self.open_folder_button.setVisible(True)
        self.convert_button.setEnabled(True)
        self.select_button.setEnabled(True)

    def open_output_folder(self):
        if sys.platform.startswith('win'):
            os.startfile(self.output_folder)
        elif sys.platform.startswith('darwin'):
            subprocess.run(['open', self.output_folder])
        else:
            subprocess.run(['xdg-open', self.output_folder])

    def check_dependencies(self):
        if not shutil.which('ffmpeg'):
            QMessageBox.critical(self, "Error", "ffmpeg not found. Please install it first.")
            return False
        return True

def show_mkv_to_mp4_converter(parent):
    dialog = MkvToMp4Converter(parent)
    dialog.exec()