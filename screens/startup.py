import os
import json
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton

RESOURCE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USER_DATA_PATH = os.path.join(RESOURCE_PATH, "resources", "user")
SETTINGS_FILE = os.path.join(USER_DATA_PATH, "settings.json")

class StartupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Welcome to Ohayo Cash Toolbox")
        self.layout = QVBoxLayout(self)

        self.label = QLabel("Please enter your name:")
        self.layout.addWidget(self.label)

        self.name_input = QLineEdit()
        self.layout.addWidget(self.name_input)

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.save_name)
        self.layout.addWidget(self.submit_button)

    def save_name(self):
        name = self.name_input.text().strip()
        if name:
            os.makedirs(USER_DATA_PATH, exist_ok=True)
            with open(SETTINGS_FILE, 'w') as f:
                json.dump({"user_name": name}, f)
            self.accept()
        else:
            self.label.setText("Please enter a valid name:")

def get_user_name():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
            return settings.get("user_name", "")
    return ""