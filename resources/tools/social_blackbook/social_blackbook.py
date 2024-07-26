import os
import json
import shutil
from datetime import datetime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
                               QStackedWidget, QPushButton, QLabel, QLineEdit, 
                               QTextEdit, QMessageBox, QFileDialog, QInputDialog,
                               QScrollArea, QFormLayout, QTabWidget, QDialog,
                               QFrame, QGridLayout, QDateEdit, QCalendarWidget,
                               QComboBox, QListView)
from PySide6.QtGui import QIcon, QPixmap, QDesktopServices, QFont
from PySide6.QtCore import Qt, Signal, QSettings, QDate, QUrl, QSize

class ContactListItem(QWidget):
    def __init__(self, contact, parent=None):
        super().__init__(parent)
        self.contact_name = contact.name
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        
        name_label = QLabel(self.contact_name)
        font = QFont("Orbitron", 10)
        name_label.setFont(font)
        layout.addWidget(name_label)
        
        for tag in contact.tags:
            tag_label = QLabel(f"[{tag}]")
            tag_label.setStyleSheet("color: #888; margin-left: 5px;")
            layout.addWidget(tag_label)
        
        layout.addStretch()

class Contact:
    def __init__(self, name, folder_path):
        self.name = name
        self.folder_path = folder_path
        self.info = {
            "Full Name": "",
            "Date of Birth": "",
            "Hometown": "",
            "Address": "",
            "Phone Number": "",
            "Email Address": ""
        }
        self.memories = []
        self.likes = []
        self.dislikes = []
        self.social_media = {}
        self.photo_path = ""
        self.important_dates = []
        self.tags = []
        self.load_data()

    def load_data(self):
        info_path = os.path.join(self.folder_path, "info.json")
        if os.path.exists(info_path):
            with open(info_path, 'r') as f:
                loaded_info = json.load(f)
                self.info.update(loaded_info)
        
        memories_path = os.path.join(self.folder_path, "memories.json")
        if os.path.exists(memories_path):
            with open(memories_path, 'r') as f:
                self.memories = json.load(f)
        
        likes_dislikes_path = os.path.join(self.folder_path, "likes_dislikes.json")
        if os.path.exists(likes_dislikes_path):
            with open(likes_dislikes_path, 'r') as f:
                data = json.load(f)
                self.likes = data.get("likes", [])
                self.dislikes = data.get("dislikes", [])
        
        social_media_path = os.path.join(self.folder_path, "social_media.json")
        if os.path.exists(social_media_path):
            with open(social_media_path, 'r') as f:
                self.social_media = json.load(f)

        photo_path = os.path.join(self.folder_path, "photo.jpg")
        if os.path.exists(photo_path):
            self.photo_path = photo_path

        dates_path = os.path.join(self.folder_path, "important_dates.json")
        if os.path.exists(dates_path):
            with open(dates_path, 'r') as f:
                self.important_dates = json.load(f)

        tags_path = os.path.join(self.folder_path, "tags.json")
        if os.path.exists(tags_path):
            with open(tags_path, 'r') as f:
                self.tags = json.load(f)

    def save_data(self):
        os.makedirs(self.folder_path, exist_ok=True)
        
        with open(os.path.join(self.folder_path, "info.json"), 'w') as f:
            json.dump(self.info, f)
        
        with open(os.path.join(self.folder_path, "memories.json"), 'w') as f:
            json.dump(self.memories, f)
        
        with open(os.path.join(self.folder_path, "likes_dislikes.json"), 'w') as f:
            json.dump({"likes": self.likes, "dislikes": self.dislikes}, f)
        
        with open(os.path.join(self.folder_path, "social_media.json"), 'w') as f:
            json.dump(self.social_media, f)

        with open(os.path.join(self.folder_path, "important_dates.json"), 'w') as f:
            json.dump(self.important_dates, f)

        with open(os.path.join(self.folder_path, "tags.json"), 'w') as f:
            json.dump(self.tags, f)

    def set_photo(self, photo_path):
        if photo_path:
            new_photo_path = os.path.join(self.folder_path, "photo.jpg")
            shutil.copy(photo_path, new_photo_path)
            self.photo_path = new_photo_path

    def ensure_folders_exist(self):
        folders = ["Photos", "Videos", "Lewd"]
        for folder in folders:
            os.makedirs(os.path.join(self.folder_path, folder), exist_ok=True)

class SocialBlackbook(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Social Blackbook")
        self.contacts = {}
        self.social_folder = self.get_social_folder()
        self.setup_ui()
        self.load_contacts()

    def get_social_folder(self):
        # Get the path to the main user folder
        user_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "user")
        settings_path = os.path.join(user_folder, "settings.json")

        # Ensure the user folder exists
        os.makedirs(user_folder, exist_ok=True)

        # If settings file doesn't exist, create it with default values
        if not os.path.exists(settings_path):
            default_settings = {
                "user_name": "Cassius",
                "music_player_first_launch": False,
                "volume": 100,
                "social_folder": ""
            }
            with open(settings_path, 'w') as f:
                json.dump(default_settings, f, indent=4)

        # Load existing settings
        with open(settings_path, 'r') as f:
            existing_settings = json.load(f)

        social_folder = existing_settings.get("social_folder")
        if not social_folder:
            social_folder = QFileDialog.getExistingDirectory(self, "Select Social Folder")
            if social_folder:
                existing_settings["social_folder"] = social_folder
                with open(settings_path, 'w') as f:
                    json.dump(existing_settings, f, indent=4)
            else:
                QMessageBox.critical(self, "Error", "No folder selected. The Social Blackbook will not function correctly.")
                return None
        return social_folder

    def setup_ui(self):
        layout = QHBoxLayout(self)
        
        # Left panel (contact list)
        left_panel = QFrame()
        left_panel.setFrameShape(QFrame.StyledPanel)
        left_panel_layout = QVBoxLayout(left_panel)
        self.contact_list = QListWidget()
        self.contact_list.itemClicked.connect(self.show_contact_details)
        left_panel_layout.addWidget(self.contact_list)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search contacts...")
        self.search_bar.textChanged.connect(self.filter_contacts)
        left_panel_layout.addWidget(self.search_bar)

        add_button = QPushButton("+")
        add_button.clicked.connect(self.add_contact)
        left_panel_layout.addWidget(add_button)

        layout.addWidget(left_panel, 1)

        # Right panel (contact details)
        self.detail_stack = QStackedWidget()
        layout.addWidget(self.detail_stack, 2)

    def load_contacts(self):
        if not self.social_folder:
            return
        for entry in os.scandir(self.social_folder):
            if entry.is_dir():
                contact = Contact(entry.name, entry.path)
                contact.ensure_folders_exist()
                self.contacts[entry.name] = contact
                self.add_contact_to_list(contact)

    def add_contact_to_list(self, contact):
        item = QListWidgetItem(self.contact_list)
        item_widget = ContactListItem(contact)
        item.setSizeHint(item_widget.sizeHint())
        self.contact_list.setItemWidget(item, item_widget)

    def filter_contacts(self, text):
        for i in range(self.contact_list.count()):
            item = self.contact_list.item(i)
            contact = self.contacts[item.text()]
            if text.lower() in item.text().lower() or any(text.lower() in tag.lower() for tag in contact.tags):
                item.setHidden(False)
            else:
                item.setHidden(True)

    def add_contact(self):
        name, ok = QInputDialog.getText(self, "Add Contact", "Enter contact name:")
        if ok and name:
            folder_name = name.lower().replace(" ", "_")
            folder_path = os.path.join(self.social_folder, folder_name)
            if os.path.exists(folder_path):
                QMessageBox.warning(self, "Warning", f"Contact '{name}' already exists.")
                return
            contact = Contact(name, folder_path)
            contact.ensure_folders_exist()
            contact.save_data()
            self.contacts[name] = contact
            self.add_contact_to_list(contact)

    def show_contact_details(self, item):
        contact_widget = self.contact_list.itemWidget(item)
        if not contact_widget:
            print("Error: No widget found for the selected item")
            return

        name = getattr(contact_widget, 'contact_name', '')
        if not name:
            print(f"Error: Unable to retrieve contact name from widget: {contact_widget}")
            return

        contact = self.contacts.get(name)
        if not contact:
            print(f"Error: No contact found for name: {name}")
            return

        # Rest of the method remains the same
        detail_widget = QWidget()
        layout = QVBoxLayout(detail_widget)

        # Top section: Photo and Basic Info
        top_section = QFrame()
        top_section.setFrameShape(QFrame.StyledPanel)
        top_section_layout = QHBoxLayout(top_section)

        # Photo
        photo_frame = QFrame()
        photo_frame.setFixedSize(200, 200)
        photo_frame.setFrameShape(QFrame.StyledPanel)
        photo_layout = QVBoxLayout(photo_frame)
        photo_label = QLabel()
        if contact.photo_path:
            pixmap = QPixmap(contact.photo_path)
            photo_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            photo_label.setAlignment(Qt.AlignCenter)
        else:
            photo_label.setText("No Photo")
        photo_layout.addWidget(photo_label)
        top_section_layout.addWidget(photo_frame)

        change_photo_button = QPushButton("+")
        change_photo_button.clicked.connect(lambda: self.change_photo(contact))
        top_section_layout.addWidget(change_photo_button)

        # Basic info
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.StyledPanel)
        info_layout = QFormLayout(info_frame)
        self.info_fields = {}
        for key in contact.info.keys():
            field = QLineEdit(contact.info[key])
            field.setReadOnly(True)
            info_layout.addRow(f"{key}:", field)
            self.info_fields[key] = field

        edit_info_button = QPushButton("✎")
        edit_info_button.clicked.connect(self.toggle_info_edit_mode)
        info_layout.addRow(edit_info_button)

        self.save_info_button = QPushButton("✓")
        self.save_info_button.clicked.connect(lambda: self.save_info(contact))
        self.save_info_button.hide()
        info_layout.addRow(self.save_info_button)

        top_section_layout.addWidget(info_frame)
        layout.addWidget(top_section)

        # Tabs for other information
        tabs = QTabWidget()

        # Memories tab
        memories_tab = self.create_expandable_list_tab(contact.memories, "Memory")
        tabs.addTab(memories_tab, "Memories")

        # Likes tab
        likes_tab = self.create_expandable_list_tab(contact.likes, "Like")
        tabs.addTab(likes_tab, "Likes")

        # Dislikes tab
        dislikes_tab = self.create_expandable_list_tab(contact.dislikes, "Dislike")
        tabs.addTab(dislikes_tab, "Dislikes")

        # Social Media tab
        social_media_tab = self.create_social_media_tab(contact)
        tabs.addTab(social_media_tab, "Social Media")

        # Important Dates tab
        dates_tab = self.create_important_dates_tab(contact)
        tabs.addTab(dates_tab, "Important Dates")

        # Photos tab
        photos_tab = self.create_media_tab(contact, "Photos")
        tabs.addTab(photos_tab, "Photos")

        # Videos tab
        videos_tab = self.create_media_tab(contact, "Videos")
        tabs.addTab(videos_tab, "Videos")

        # Lewd tab
        lewd_tab = self.create_media_tab(contact, "Lewd")
        tabs.addTab(lewd_tab, "Lewd")

        # Tags tab
        tags_tab = self.create_tags_tab(contact)
        tabs.addTab(tags_tab, "Tags")

        layout.addWidget(tabs)

        # Save button
        save_button = QPushButton("Save Changes")
        save_button.clicked.connect(lambda: self.save_changes(contact))
        layout.addWidget(save_button)

        scroll_area = QScrollArea()
        scroll_area.setWidget(detail_widget)
        scroll_area.setWidgetResizable(True)

        self.detail_stack.addWidget(scroll_area)
        self.detail_stack.setCurrentWidget(scroll_area)

    def create_expandable_list_tab(self, items, item_type):
        tab = QScrollArea()
        content = QWidget()
        layout = QVBoxLayout(content)
        
        for item in items:
            item_widget = self.create_expandable_text_widget(item)
            layout.addWidget(item_widget)
        
        add_button = QPushButton("+")
        add_button.clicked.connect(lambda: self.add_list_item(layout, f"New {item_type}"))
        layout.addWidget(add_button)
        
        tab.setWidget(content)
        tab.setWidgetResizable(True)
        return tab

    def create_expandable_text_widget(self, text):
        widget = QFrame()
        widget.setFrameShape(QFrame.StyledPanel)
        layout = QVBoxLayout(widget)
        
        label = QLabel(text)
        label.setWordWrap(True)
        layout.addWidget(label)
        
        edit = QTextEdit(text)
        edit.setVisible(False)
        layout.addWidget(edit)
        
        expand_button = QPushButton("Expand")
        expand_button.clicked.connect(lambda: self.toggle_expanded(label, edit, expand_button))
        layout.addWidget(expand_button)
        
        return widget

    def toggle_expanded(self, label, edit, button):
        if edit.isVisible():
            label.setText(edit.toPlainText())
            label.show()
            edit.hide()
            button.setText("Expand")
        else:
            label.hide()
            edit.show()
            button.setText("Collapse")

    def create_social_media_tab(self, contact):
        tab = QScrollArea()
        content = QWidget()
        layout = QVBoxLayout(content)

        for platform, link in contact.social_media.items():
            social_media_widget = self.create_social_media_widget(platform, link)
            layout.addWidget(social_media_widget)

        add_button = QPushButton("+")
        add_button.clicked.connect(lambda: self.add_social_media(contact, layout))
        layout.addWidget(add_button)

        tab.setWidget(content)
        tab.setWidgetResizable(True)
        return tab

    def create_social_media_widget(self, platform, link):
        widget = QFrame()
        widget.setFrameShape(QFrame.StyledPanel)
        layout = QHBoxLayout(widget)

        platform_edit = QLineEdit(platform)
        platform_edit.setFixedWidth(100)
        layout.addWidget(platform_edit)

        link_edit = QLineEdit(link)
        layout.addWidget(link_edit)

        open_button = QPushButton("Open")
        open_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(link)))
        layout.addWidget(open_button)

        return widget

    def add_social_media(self, contact, layout):
        platform, ok = QInputDialog.getText(self, "Add Social Media", "Enter platform name:")
        if ok and platform:
            link, ok = QInputDialog.getText(self, "Add Social Media", f"Enter {platform} link:")
            if ok and link:
                social_media_widget = self.create_social_media_widget(platform, link)
                layout.insertWidget(layout.count() - 1, social_media_widget)
                contact.social_media[platform] = link

    def create_important_dates_tab(self, contact):
        tab = QScrollArea()
        content = QWidget()
        layout = QVBoxLayout(content)
        
        for date_item in contact.important_dates:
            date_widget = self.create_date_widget(date_item)
            layout.addWidget(date_widget)
        
        add_button = QPushButton("+")
        add_button.clicked.connect(lambda: self.add_important_date(layout, contact))
        layout.addWidget(add_button)
        
        tab.setWidget(content)
        tab.setWidgetResizable(True)
        return tab

    def create_date_widget(self, date_item):
        widget = QFrame()
        widget.setFrameShape(QFrame.StyledPanel)
        layout = QHBoxLayout(widget)
        
        date_edit = QDateEdit(QDate.fromString(date_item['date'], "yyyy-MM-dd"))
        date_edit.setDisplayFormat("yyyy-MM-dd")
        date_edit.setFixedWidth(160)  # Adjust width to ensure full date is visible
        layout.addWidget(date_edit)
        
        description = QLineEdit(date_item['description'])
        layout.addWidget(description, 1)  # Give the description field more space
        
        return widget

    def add_important_date(self, layout, contact):
        new_date = {'date': QDate.currentDate().toString("yyyy-MM-dd"), 'description': "New important date"}
        contact.important_dates.append(new_date)
        date_widget = self.create_date_widget(new_date)
        layout.insertWidget(layout.count() - 1, date_widget)

    def create_media_tab(self, contact, media_type):
        tab = QScrollArea()
        content = QWidget()
        layout = QVBoxLayout(content)

        media_folder = os.path.join(contact.folder_path, media_type)
        
        add_button = QPushButton("+")
        add_button.clicked.connect(lambda: self.add_media_file(contact, media_type))
        layout.addWidget(add_button)

        self.media_layout = QGridLayout()
        self.populate_media_grid(contact, media_type)
        layout.addLayout(self.media_layout)

        tab.setWidget(content)
        tab.setWidgetResizable(True)
        return tab

    def populate_media_grid(self, contact, media_type):
        media_folder = os.path.join(contact.folder_path, media_type)
        layout = self.media_layout

        for i in reversed(range(layout.count())): 
            layout.itemAt(i).widget().setParent(None)

        files = sorted(os.listdir(media_folder), key=lambda f: os.path.getmtime(os.path.join(media_folder, f)), reverse=True)
        
        size = QSize(200, 200)  # Fixed size for all icons

        for i, file_name in enumerate(files):
            file_path = os.path.join(media_folder, file_name)
            media_widget = self.create_media_widget(file_path, size)
            layout.addWidget(media_widget, i // 4, i % 4)

    def create_media_widget(self, file_path, size):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        icon = QIcon(file_path)
        image_button = QPushButton()
        image_button.setIcon(icon)
        image_button.setIconSize(size)
        image_button.setFixedSize(size)
        image_button.setStyleSheet("QPushButton { border: none; }")
        layout.addWidget(image_button)

        button_layout = QHBoxLayout()
        open_button = QPushButton("Open")
        open_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(file_path)))
        button_layout.addWidget(open_button)

        explore_button = QPushButton("Explore")
        explore_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(file_path))))
        button_layout.addWidget(explore_button)

        layout.addLayout(button_layout)
        return widget

    def add_media_file(self, contact, media_type):
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, f"Select {media_type} File")
        if file_path:
            destination = os.path.join(contact.folder_path, media_type, os.path.basename(file_path))
            shutil.copy(file_path, destination)
            self.populate_media_grid(contact, media_type)

    def create_tags_tab(self, contact):
        tab = QScrollArea()
        content = QWidget()
        layout = QVBoxLayout(content)

        for tag in contact.tags:
            tag_widget = self.create_tag_widget(tag, contact)
            layout.addWidget(tag_widget)

        add_button = QPushButton("+")
        add_button.clicked.connect(lambda: self.add_tag(contact, layout))
        layout.addWidget(add_button)

        tab.setWidget(content)
        tab.setWidgetResizable(True)
        return tab

    def create_tag_widget(self, tag, contact):
        widget = QFrame()
        widget.setFrameShape(QFrame.StyledPanel)
        layout = QHBoxLayout(widget)

        label = QLabel(tag)
        layout.addWidget(label)

        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(lambda: self.remove_tag(contact, tag, widget))
        layout.addWidget(remove_button)

        return widget

    def add_tag(self, contact, layout):
        tag, ok = QInputDialog.getText(self, "Add Tag", "Enter tag:")
        if ok and tag:
            contact.tags.append(tag)
            tag_widget = self.create_tag_widget(tag, contact)
            layout.insertWidget(layout.count() - 1, tag_widget)
            self.update_contact_item(contact)

    def remove_tag(self, contact, tag, widget):
        contact.tags.remove(tag)
        widget.setParent(None)
        widget.deleteLater()
        self.update_contact_item(contact)

    def update_contact_item(self, contact):
        for i in range(self.contact_list.count()):
            item = self.contact_list.item(i)
            if self.contact_list.itemWidget(item).findChild(QLabel).text() == contact.name:
                item_widget = ContactListItem(contact)
                item.setSizeHint(item_widget.sizeHint())
                self.contact_list.setItemWidget(item, item_widget)
                break

    def toggle_info_edit_mode(self):
        edit_mode = self.save_info_button.isVisible()
        for field in self.info_fields.values():
            field.setReadOnly(edit_mode)
        self.save_info_button.setVisible(not edit_mode)

    def save_info(self, contact):
        for key, field in self.info_fields.items():
            contact.info[key] = field.text()
        contact.save_data()
        self.toggle_info_edit_mode()
        QMessageBox.information(self, "Success", "Contact info saved successfully!")

    def change_photo(self, contact):
        file_dialog = QFileDialog(self)
        photo_path, _ = file_dialog.getOpenFileName(self, "Select Photo", "", "Image files (*.jpg *.png)")
        if photo_path:
            contact.set_photo(photo_path)
            self.show_contact_details(self.contact_list.currentItem())

    def save_changes(self, contact):
        # Save memories, likes, dislikes
        for tab_name, attribute in [("Memories", "memories"), ("Likes", "likes"), ("Dislikes", "dislikes")]:
            tab = self.findChild(QScrollArea, tab_name)
            if tab:
                items = []
                for i in range(tab.widget().layout().count() - 1):  # -1 to exclude the add button
                    widget = tab.widget().layout().itemAt(i).widget()
                    items.append(self.get_widget_text(widget))
                setattr(contact, attribute, items)

        # Save social media
        social_media_tab = self.findChild(QScrollArea, "Social Media")
        if social_media_tab:
            contact.social_media = {}
            for i in range(social_media_tab.widget().layout().count() - 1):
                widget = social_media_tab.widget().layout().itemAt(i).widget()
                platform = widget.findChild(QLineEdit).text()
                link = widget.findChildren(QLineEdit)[1].text()
                contact.social_media[platform] = link

        # Save important dates
        dates_tab = self.findChild(QScrollArea, "Important Dates")
        if dates_tab:
            contact.important_dates = []
            for i in range(dates_tab.widget().layout().count() - 1):
                widget = dates_tab.widget().layout().itemAt(i).widget()
                date_edit = widget.findChild(QDateEdit)
                description = widget.findChild(QLineEdit)
                if date_edit and description:
                    contact.important_dates.append({
                        'date': date_edit.date().toString("yyyy-MM-dd"),
                        'description': description.text()
                    })

        contact.save_data()
        QMessageBox.information(self, "Success", "Changes saved successfully!")

    def get_widget_text(self, widget):
        edit = widget.findChild(QTextEdit)
        return edit.toPlainText() if edit.isVisible() else widget.findChild(QLabel).text()

def show_social_blackbook(parent):
    return SocialBlackbook(parent)