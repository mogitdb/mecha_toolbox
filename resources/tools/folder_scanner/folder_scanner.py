import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QLineEdit, QDialogButtonBox, QTextEdit, QFileDialog)

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

    input_label = QLabel("Select the directory to scan:")
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
            show_scan_result(parent, result)
        else:
            show_error_message(parent, "No directory selected")

def select_folder(input_field):
    folder = QFileDialog.getExistingDirectory()
    if folder:
        input_field.setText(folder)

def show_scan_result(parent, result):
    dialog = QDialog(parent)
    dialog.setWindowTitle("Scan Result")
    layout = QVBoxLayout(dialog)

    result_text = QTextEdit()
    result_text.setPlainText(result)
    result_text.setReadOnly(True)
    layout.addWidget(result_text)

    button_box = QDialogButtonBox(QDialogButtonBox.Ok)
    button_box.accepted.connect(dialog.accept)
    layout.addWidget(button_box)

    dialog.exec_()

def show_error_message(parent, message):
    error_dialog = QDialog(parent)
    error_dialog.setWindowTitle("Error")
    layout = QVBoxLayout(error_dialog)
    layout.addWidget(QLabel(message))
    button_box = QDialogButtonBox(QDialogButtonBox.Ok)
    button_box.accepted.connect(error_dialog.accept)
    layout.addWidget(button_box)
    error_dialog.exec_()