import os
import json
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QListWidget, QListWidgetItem, QLabel
import feedparser

RESOURCE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USER_DATA_PATH = os.path.join(RESOURCE_PATH, "resources", "user")
FEEDS_FILE = os.path.join(USER_DATA_PATH, "feeds.json")

class RSSUpdatesScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.feeds = []

        # Add feed input
        input_layout = QHBoxLayout()
        self.feed_input = QLineEdit()
        self.add_button = QPushButton("+")
        self.add_button.clicked.connect(self.add_feed)
        input_layout.addWidget(self.feed_input)
        input_layout.addWidget(self.add_button)
        self.layout.addLayout(input_layout)

        # Feed list
        self.feed_list = QListWidget()
        self.layout.addWidget(self.feed_list)

        self.load_feeds()
        self.update_feed_list()

    def load_feeds(self):
        if os.path.exists(FEEDS_FILE):
            with open(FEEDS_FILE, 'r') as f:
                self.feeds = json.load(f)

    def save_feeds(self):
        os.makedirs(USER_DATA_PATH, exist_ok=True)
        with open(FEEDS_FILE, 'w') as f:
            json.dump(self.feeds, f)

    def add_feed(self):
        url = self.feed_input.text().strip()
        if url and url not in self.feeds:
            self.feeds.append(url)
            self.save_feeds()
            self.update_feed_list()
            self.feed_input.clear()

    def remove_feed(self, item):
        url = item.text().split(' - ')[0]
        self.feeds.remove(url)
        self.save_feeds()
        self.update_feed_list()

    def update_feed_list(self):
        self.feed_list.clear()
        for feed in self.feeds:
            try:
                d = feedparser.parse(feed)
                title = d.feed.title
                item = QListWidgetItem(f"{feed} - {title}")
                self.feed_list.addItem(item)
            except:
                item = QListWidgetItem(f"{feed} - Unable to parse")
                self.feed_list.addItem(item)

        # Add remove buttons
        for i in range(self.feed_list.count()):
            item = self.feed_list.item(i)
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.addWidget(QLabel(item.text()))
            remove_button = QPushButton("-")
            remove_button.clicked.connect(lambda _, item=item: self.remove_feed(item))
            layout.addWidget(remove_button)
            self.feed_list.setItemWidget(item, widget)