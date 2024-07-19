import os
import sys
import subprocess
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QLineEdit, QDialogButtonBox, QTextEdit,
                               QFileDialog, QApplication)
from PySide6.QtCore import Qt

def scan_folder_structure(root_path):
    structure = []
    for root, dirs, files in os.walk(root_path):
        level = root.replace(root_path, '').count(os.sep)
        indent = ' ' * 4 * (level)
        structure.append(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            structure.append(f'{subindent}{f}')
    return '\n'.join(structure)

def show_folder_scanner_dialog(parent):
    dialog = QDialog(parent)
    dialog.setWindowTitle("Folder Scanner")
    layout = QVBoxLayout(dialog)

    input_label = QLabel("Enter the directory path to scan:")
    layout.addWidget(input_label)

    input_layout = QHBoxLayout()
    input_field = QLineEdit()
    input_layout.addWidget(input_field)

    browse_button = QPushButton("Browse")
    browse_button.clicked.connect(lambda: select_folder(input_field))
    input_layout.addWidget(browse_button)

    layout.addLayout(input_layout)

    button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    button_box.accepted.connect(dialog.accept)
    button_box.rejected.connect(dialog.reject)
    layout.addWidget(button_box)

    if dialog.exec_() == QDialog.Accepted:
        directory = input_field.text()
        if directory:
            result = scan_folder_structure(directory)
            save_and_show_scan_result(parent, result, directory)
        else:
            show_error_message(parent, "No directory selected")

def select_folder(input_field):
    folder = QFileDialog.getExistingDirectory()
    if folder:
        input_field.setText(folder)

def save_and_show_scan_result(parent, result, scanned_directory):
    documents_path = os.path.expanduser("~/Documents")
    output_folder = os.path.join(documents_path, "folder_scanner")
    os.makedirs(output_folder, exist_ok=True)

    scanned_folder_name = os.path.basename(scanned_directory)
    output_file = os.path.join(output_folder, f"{scanned_folder_name}_scan.txt")

    with open(output_file, 'w') as f:
        f.write(result)

    show_scan_result(parent, result, output_file, output_folder)

def show_scan_result(parent, result, output_file, output_folder):
    dialog = QDialog(parent)
    dialog.setWindowTitle("Scan Result")
    layout = QVBoxLayout(dialog)

    result_text = QTextEdit()
    result_text.setPlainText(result)
    result_text.setReadOnly(True)
    layout.addWidget(result_text)

    button_layout = QHBoxLayout()
    
    copy_button = QPushButton("Copy to Clipboard")
    copy_button.clicked.connect(lambda: QApplication.clipboard().setText(result))
    button_layout.addWidget(copy_button)

    open_file_button = QPushButton("Open Output File")
    open_file_button.clicked.connect(lambda: open_file(output_file))
    button_layout.addWidget(open_file_button)

    open_folder_button = QPushButton("Open Output Folder")
    open_folder_button.clicked.connect(lambda: open_folder(output_folder))
    button_layout.addWidget(open_folder_button)

    close_button = QPushButton("Close")
    close_button.clicked.connect(dialog.accept)
    button_layout.addWidget(close_button)

    layout.addLayout(button_layout)

    dialog.exec_()

def open_file(file_path):
    if sys.platform == 'win32':
        os.startfile(file_path)
    elif sys.platform == 'darwin':
        subprocess.run(['open', file_path])
    else:
        subprocess.run(['xdg-open', file_path])

def open_folder(folder_path):
    if sys.platform == 'win32':
        os.startfile(folder_path)
    elif sys.platform == 'darwin':
        subprocess.run(['open', folder_path])
    else:
        subprocess.run(['xdg-open', folder_path])

def show_error_message(parent, message):
    error_dialog = QDialog(parent)
    error_dialog.setWindowTitle("Error")
    layout = QVBoxLayout(error_dialog)
    layout.addWidget(QLabel(message))
    button_box = QDialogButtonBox(QDialogButtonBox.Ok)
    button_box.accepted.connect(error_dialog.accept)
    layout.addWidget(button_box)
    error_dialog.exec_()