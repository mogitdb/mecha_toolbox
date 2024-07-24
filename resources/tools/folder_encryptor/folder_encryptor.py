import subprocess
import sys
import os
import threading
import zipfile
import secrets
import string
import datetime
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QLineEdit, QMessageBox, QFileDialog, QProgressBar)
from PySide6.QtCore import Signal, QThread
import pyzipper

class EncryptionThread(QThread):
    update_progress = Signal(str)
    encryption_complete = Signal(str, str, str)
    encryption_failed = Signal(str)

    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path

    def run(self):
        try:
            password = generate_password()
            documents_path = os.path.expanduser("~/Documents")
            app_folder = os.path.join(documents_path, "ZipGen")
            if not os.path.exists(app_folder):
                os.makedirs(app_folder)

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"encrypted_folder_{timestamp}.zip"
            output_path = os.path.join(app_folder, output_filename)

            self.update_progress.emit("Encrypting folder...")
            zip_encrypt_folder(self.folder_path, output_path, password)

            log_file = os.path.join(app_folder, "encryption_log.txt")
            log_operation(self.folder_path, output_path, password, log_file)

            self.encryption_complete.emit(password, output_path, log_file)
        except Exception as e:
            self.encryption_failed.emit(str(e))

def generate_password(length=16):
    symbols = string.punctuation
    digits = string.digits
    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    
    password = [
        secrets.choice(symbols),
        secrets.choice(digits),
        secrets.choice(uppercase),
        secrets.choice(lowercase)
    ]
    
    all_characters = symbols + digits + uppercase + lowercase
    password += [secrets.choice(all_characters) for _ in range(length - 4)]
    
    secrets.SystemRandom().shuffle(password)
    
    return ''.join(password)

def zip_encrypt_folder(folder_path, output_path, password):
    with pyzipper.AESZipFile(output_path, 'w', compression=pyzipper.ZIP_LZMA, encryption=pyzipper.WZ_AES) as zf:
        zf.setpassword(password.encode())
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zf.write(file_path, arcname)

def log_operation(folder_path, output_path, password, log_file):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] Encrypted: {folder_path} -> {output_path} (Password: {password})\n"
    with open(log_file, "a") as f:
        f.write(log_entry)

class FolderEncryptorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Folder Encryptor")
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.folder_label = QLabel("Select a folder to encrypt:")
        layout.addWidget(self.folder_label)

        folder_layout = QHBoxLayout()
        self.folder_entry = QLineEdit()
        folder_layout.addWidget(self.folder_entry)
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.browse_button)
        layout.addLayout(folder_layout)

        self.encrypt_button = QPushButton("Encrypt")
        self.encrypt_button.clicked.connect(self.start_encryption)
        layout.addWidget(self.encrypt_button)

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

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder to Encrypt")
        if folder_path:
            self.folder_entry.setText(folder_path)

    def start_encryption(self):
        folder_path = self.folder_entry.text()
        if not folder_path:
            QMessageBox.warning(self, "Error", "Please select a folder to encrypt.")
            return

        self.encrypt_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_label.setText("Starting encryption...")

        self.encryption_thread = EncryptionThread(folder_path)
        self.encryption_thread.update_progress.connect(self.update_progress_label)
        self.encryption_thread.encryption_complete.connect(self.encryption_complete)
        self.encryption_thread.encryption_failed.connect(self.encryption_failed)
        self.encryption_thread.start()

    def update_progress_label(self, message):
        self.progress_label.setText(message)

    def encryption_complete(self, password, output_path, log_file):
        self.progress_bar.setVisible(False)
        self.encrypt_button.setEnabled(True)
        self.view_output_button.setVisible(True)
        self.progress_label.setText("Encryption complete")

        message = (f"Folder encrypted successfully!\n"
                   f"Password: {password}\n"
                   f"Encrypted file: {output_path}\n"
                   f"Log file: {log_file}")
        QMessageBox.information(self, "Success", message)

    def encryption_failed(self, error_message):
        self.progress_bar.setVisible(False)
        self.encrypt_button.setEnabled(True)
        self.progress_label.setText("Encryption failed")
        QMessageBox.critical(self, "Error", f"An error occurred: {error_message}")

    def view_output_folder(self):
        output_folder = os.path.expanduser("~/Documents/ZipGen")
        if sys.platform == 'win32':
            os.startfile(output_folder)
        elif sys.platform == 'darwin':
            subprocess.run(['open', output_folder])
        else:
            subprocess.run(['xdg-open', output_folder])

def show_folder_encryptor_dialog(parent):
    dialog = FolderEncryptorDialog(parent)
    dialog.exec()