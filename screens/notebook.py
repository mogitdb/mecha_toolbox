import os
import json
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTreeView, QFileSystemModel, QFileDialog

RESOURCE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USER_DATA_PATH = os.path.join(RESOURCE_PATH, "resources", "user")
VAULTS_FILE = os.path.join(USER_DATA_PATH, "vaults.json")

class NotebookScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.vaults = []
        
        # Add vault buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("+")
        self.add_button.clicked.connect(self.add_vault)
        self.remove_button = QPushButton("-")
        self.remove_button.clicked.connect(self.remove_vault)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        self.layout.addLayout(button_layout)

        # Vault tree view
        self.tree_view = QTreeView()
        self.layout.addWidget(self.tree_view)

        self.load_vaults()
        self.update_vault_view()

    def load_vaults(self):
        if os.path.exists(VAULTS_FILE):
            with open(VAULTS_FILE, 'r') as f:
                self.vaults = json.load(f)

    def save_vaults(self):
        os.makedirs(USER_DATA_PATH, exist_ok=True)
        with open(VAULTS_FILE, 'w') as f:
            json.dump(self.vaults, f)

    def add_vault(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Obsidian Vault")
        if folder and folder not in self.vaults:
            self.vaults.append(folder)
            self.save_vaults()
            self.update_vault_view()

    def remove_vault(self):
        selected = self.tree_view.selectedIndexes()
        if selected:
            index = selected[0]
            path = self.model.filePath(index)
            if path in self.vaults:
                self.vaults.remove(path)
                self.save_vaults()
                self.update_vault_view()

    def update_vault_view(self):
        if self.vaults:
            self.model = QFileSystemModel()
            self.model.setRootPath(self.vaults[0])
            self.tree_view.setModel(self.model)
            self.tree_view.setRootIndex(self.model.index(self.vaults[0]))
        else:
            self.tree_view.setModel(None)