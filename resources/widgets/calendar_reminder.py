from PySide6.QtWidgets import (QWidget, QVBoxLayout, QCalendarWidget, QLabel, 
                               QHBoxLayout, QScrollArea)
from PySide6.QtGui import QPixmap, QPainter, QColor
from PySide6.QtCore import Qt, QDate, QSize, QRect

class CalendarReminderWidget(QWidget):
    def __init__(self, social_blackbook=None):
        super().__init__()
        self.social_blackbook = social_blackbook
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        layout.addWidget(self.calendar)
        
        self.upcoming_events = QScrollArea()
        self.upcoming_events.setWidgetResizable(True)
        self.upcoming_events_content = QWidget()
        self.upcoming_events_layout = QVBoxLayout(self.upcoming_events_content)
        self.upcoming_events.setWidget(self.upcoming_events_content)
        layout.addWidget(self.upcoming_events)
        
        if self.social_blackbook:
            self.update_events()

    def update_events(self):
        if not self.social_blackbook:
            return

        events = []
        for contact in self.social_blackbook.contacts.values():
            for date_item in contact.important_dates:
                date = QDate.fromString(date_item['date'], "yyyy-MM-dd")
                events.append((date, contact, date_item['description']))
        
        events.sort(key=lambda x: x[0])
        
        # Clear previous events
        self.calendar.setDateTextFormat(QDate(), self.calendar.dateTextFormat(QDate()))
        
        # Update calendar with new events
        for date, contact, description in events:
            format = self.calendar.dateTextFormat(date)
            format.setBackground(QColor(255, 255, 0, 50))  # Light yellow background
            self.calendar.setDateTextFormat(date, format)
        
        # Update upcoming events list
        self.update_upcoming_events(events)

    def update_upcoming_events(self, events):
        # Clear previous events
        for i in reversed(range(self.upcoming_events_layout.count())):
            self.upcoming_events_layout.itemAt(i).widget().setParent(None)
        
        # Add new events
        for date, contact, description in events:
            if date >= QDate.currentDate():
                event_widget = QWidget()
                event_layout = QHBoxLayout(event_widget)
                
                if contact.photo_path:
                    photo_label = QLabel()
                    pixmap = QPixmap(contact.photo_path)
                    photo_label.setPixmap(pixmap.scaled(30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    event_layout.addWidget(photo_label)
                
                event_label = QLabel(f"{date.toString('yyyy-MM-dd')}: {contact.name} - {description}")
                event_layout.addWidget(event_label)
                
                self.upcoming_events_layout.addWidget(event_widget)

    def set_social_blackbook(self, social_blackbook):
        self.social_blackbook = social_blackbook
        self.update_events()

# Make sure the class is exported
__all__ = ['CalendarReminderWidget']