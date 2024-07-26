import sys
import os
import json
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLabel, QStatusBar, QMenu, QStackedWidget, QSlider)
from PySide6.QtGui import QFont, QIcon, QFontDatabase, QMovie
from PySide6.QtCore import Qt, QSize, QTimer, QUrl, QSettings
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

# Import screen classes
from screens.notebook import NotebookScreen
from screens.rss_updates import RSSUpdatesScreen
from screens.startup import StartupDialog, get_user_name
from resources.tools.music_player.music_player import show_music_player

# Update the base path for resources
RESOURCE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources")
TOOLS_PATH = os.path.join(RESOURCE_PATH, "tools")
USER_FOLDER = os.path.expanduser("~/.mecha_toolbox")
if not os.path.exists(USER_FOLDER):
    os.makedirs(USER_FOLDER)

# Add TOOLS_PATH and RESOURCE_PATH to sys.path
sys.path.append(TOOLS_PATH)
sys.path.append(RESOURCE_PATH)

# Import and run library check
from resources.library.library_manager import check_and_install_libraries
check_and_install_libraries()

# Import tool functions
from resources.tools.folder_scanner.folder_scanner import show_folder_scanner_dialog
from resources.tools.video_format_converter.video_format_converter import show_video_format_converter
from resources.tools.ytdl.ytdl import show_youtube_downloader
from resources.tools.folder_encryptor.folder_encryptor import show_folder_encryptor_dialog
from resources.tools.pdf_scraper.pdf_scraper import show_pdf_scraper_dialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.user_name = self.get_or_ask_user_name()
        self.setWindowTitle("Mecha's Toolbox")
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e; 
                color: white;
            }
            QMenu {
                background-color: #2e2e2e;
                color: white;
                border: 1px solid white;
            }
            QMenu::item {
                padding: 5px 20px;
            }
            QMenu::item:selected {
                background-color: #3e3e3e;
            }
        """)
        self.setWindowIcon(QIcon(os.path.join(RESOURCE_PATH, "ui", "icon.png")))
        
        # Load custom font
        font_id = QFontDatabase.addApplicationFont(os.path.join(RESOURCE_PATH, "font", "Orbitron", "Orbitron-VariableFont_wght.ttf"))
        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            self.custom_font = QFont(font_family)
        else:
            self.custom_font = QFont("Arial")  # Fallback font
        
        self.setup_audio()
        self.setup_ui()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_greeting)
        self.timer.timeout.connect(self.update_gifs)
        self.timer.start(60000)  # Update every minute

        self.music_player = None

    def get_or_ask_user_name(self):
        name = get_user_name()
        if not name:
            dialog = StartupDialog(self)
            if dialog.exec_():
                name = get_user_name()
        return name

    def setup_audio(self):
        self.audio_output = QAudioOutput()
        self.media_player = QMediaPlayer()
        self.media_player.setAudioOutput(self.audio_output)
        
        # Load and set the volume before playing
        volume = self.load_volume()
        self.audio_output.setVolume(volume / 100.0)
        
        bgm_path = os.path.join(RESOURCE_PATH, "sound", "music", "bgm.mp3")
        if os.path.exists(bgm_path):
            self.media_player.setSource(QUrl.fromLocalFile(bgm_path))
            self.media_player.mediaStatusChanged.connect(self.handle_media_status_changed)
            self.media_player.play()
        else:
            print(f"Background music file not found: {bgm_path}")

    def handle_media_status_changed(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.media_player.setPosition(0)
            self.media_player.play()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Top bar
        top_bar = self.create_top_bar()
        main_layout.addLayout(top_bar)

        # Add trim below top bar
        trim = QWidget()
        trim.setFixedHeight(2)
        trim.setStyleSheet("background-color: white;")
        main_layout.addWidget(trim)

        # Stacked widget for different screens
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        # Create home screen (empty for now)
        self.home_screen = QWidget()
        self.stacked_widget.addWidget(self.home_screen)

        # Set the initial screen
        self.stacked_widget.setCurrentWidget(self.home_screen)

        self.setStatusBar(QStatusBar())

    def create_top_bar(self):
        top_bar = QHBoxLayout()
        
        self.menu_button = self.create_menu_button()
        top_bar.addWidget(self.menu_button)
        
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.go_back)
        self.back_button.setVisible(False)
        top_bar.addWidget(self.back_button)
        
        top_bar.addStretch(1)
        
        self.left_gif = QLabel()
        self.greeting_label = QLabel()
        self.greeting_label.setFont(self.custom_font)
        self.greeting_label.setStyleSheet("font-size: 24px;")
        self.right_gif = QLabel()
        
        top_bar.addWidget(self.left_gif)
        top_bar.addWidget(self.greeting_label)
        top_bar.addWidget(self.right_gif)
        
        top_bar.addStretch(1)
        
        volume_layout = QVBoxLayout()
        volume_label = QLabel("Volume")
        volume_label.setAlignment(Qt.AlignCenter)
        volume_label.setFont(self.custom_font)  # Apply custom font to volume label
        volume_layout.addWidget(volume_label)
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(self.load_volume())
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.valueChanged.connect(self.change_volume)
        volume_layout.addWidget(self.volume_slider)
        
        top_bar.addLayout(volume_layout)
        
        settings_button = self.create_settings_button()
        top_bar.addWidget(settings_button)
        
        self.update_greeting()
        self.update_gifs()
        
        return top_bar

    def create_menu_button(self):
        menu_button = QPushButton(QIcon(os.path.join(RESOURCE_PATH, "ui", "icon.png")), "")
        menu_button.setFixedSize(50, 50)
        menu_button.setIconSize(QSize(40, 40))
        menu_button.setStyleSheet("""
            QPushButton {
                background-color: transparent; 
                border: none;
            }
            QPushButton:hover {
                border: 2px solid white;
            }
        """)
        menu_button.clicked.connect(self.show_tools_menu)
        return menu_button

    def create_settings_button(self):
        settings_button = QPushButton(QIcon(os.path.join(RESOURCE_PATH, "ui", "cog.jpg")), "")
        settings_button.setFixedSize(50, 50)
        settings_button.setIconSize(QSize(40, 40))
        settings_button.setStyleSheet("background-color: transparent; border: none;")
        settings_button.clicked.connect(self.open_settings)
        return settings_button

    def update_greeting(self):
        current_hour = datetime.now().hour
        if 5 <= current_hour < 12:
            greeting = f"Ohayo {self.user_name}!"
        elif 12 <= current_hour < 18:
            greeting = f"Konnichiwa {self.user_name}!"
        else:
            greeting = f"Oyasumi {self.user_name}!"
        self.greeting_label.setText(greeting)

    def update_gifs(self):
        current_hour = datetime.now().hour
        if 5 <= current_hour < 12:
            gif_path = os.path.join(RESOURCE_PATH, "ui", "morning.gif")
        elif 12 <= current_hour < 18:
            gif_path = os.path.join(RESOURCE_PATH, "ui", "afternoon.gif")
        else:
            gif_path = os.path.join(RESOURCE_PATH, "ui", "night.gif")
        
        if os.path.exists(gif_path):
            movie = QMovie(gif_path)
            movie.setScaledSize(QSize(50, 50))
            self.left_gif.setMovie(movie)
            self.right_gif.setMovie(movie)
            movie.start()
        else:
            self.left_gif.setText("GIF")
            self.right_gif.setText("GIF")

    def change_volume(self, value):
        volume = value / 100.0
        if self.music_player and self.stacked_widget.currentWidget() == self.music_player:
            self.music_player.set_volume(value)
        else:
            self.audio_output.setVolume(volume)
        self.save_volume(value)

    def save_volume(self, value):
        settings = QSettings(os.path.join(USER_FOLDER, "settings.ini"), QSettings.IniFormat)
        settings.setValue("volume", value)

    def load_volume(self):
        settings = QSettings(os.path.join(USER_FOLDER, "settings.ini"), QSettings.IniFormat)
        return settings.value("volume", 50, type=int)

    def open_settings(self):
        # Implement settings dialog here
        pass

    def show_tools_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2e2e2e;
                color: white;
                border: 1px solid white;
            }
            QMenu::item {
                padding: 5px 20px;
            }
            QMenu::item:selected {
                background-color: #3e3e3e;
            }
        """)
        notebook_action = menu.addAction("Notebook")
        notebook_action.triggered.connect(self.show_notebook)
        rss_updates_action = menu.addAction("RSS Updates")
        rss_updates_action.triggered.connect(self.show_rss_updates)
        
        # Add other tools here
        youtube_downloader_action = menu.addAction("YouTube Downloader")
        youtube_downloader_action.triggered.connect(self.show_youtube_downloader)
        folder_scanner_action = menu.addAction("Folder Scanner")
        folder_scanner_action.triggered.connect(self.show_folder_scanner)
        video_converter_action = menu.addAction("Video Format Converter")
        video_converter_action.triggered.connect(self.show_video_format_converter)
        folder_encryptor_action = menu.addAction("Folder Encryptor")
        folder_encryptor_action.triggered.connect(self.show_folder_encryptor)
        pdf_scraper_action = menu.addAction("PDF Scraper")
        pdf_scraper_action.triggered.connect(self.show_pdf_scraper)
        music_player_action = menu.addAction("Music Player")
        music_player_action.triggered.connect(self.show_music_player)
        
        menu.exec(self.menu_button.mapToGlobal(self.menu_button.rect().bottomLeft()))

    def go_back(self):
        if self.stacked_widget.currentWidget() == self.music_player:
            self.music_player.stop_playback()
            self.media_player.play()  # Resume menu music when exiting music player
            # Restore menu music volume when leaving music player
            saved_volume = self.load_volume()
            self.audio_output.setVolume(saved_volume / 100.0)
            self.volume_slider.setValue(saved_volume)
        self.stacked_widget.setCurrentWidget(self.home_screen)
        self.back_button.setVisible(False)

    def show_notebook(self):
        notebook_screen = NotebookScreen(self.stacked_widget)
        self.stacked_widget.addWidget(notebook_screen)
        self.stacked_widget.setCurrentWidget(notebook_screen)
        self.back_button.setVisible(True)

    def show_rss_updates(self):
        rss_updates_screen = RSSUpdatesScreen(self.stacked_widget)
        self.stacked_widget.addWidget(rss_updates_screen)
        self.stacked_widget.setCurrentWidget(rss_updates_screen)
        self.back_button.setVisible(True)

    def show_youtube_downloader(self):
        show_youtube_downloader(self)

    def show_folder_scanner(self):
        show_folder_scanner_dialog(self)

    def show_video_format_converter(self):
        show_video_format_converter(self)

    def show_folder_encryptor(self):
        show_folder_encryptor_dialog(self)

    def show_pdf_scraper(self):
        show_pdf_scraper_dialog(self)

    def show_music_player(self):
        if self.music_player is None:
            self.music_player = show_music_player(self, USER_FOLDER)
            self.music_player.music_started.connect(self.on_music_player_started)
            self.music_player.music_stopped.connect(self.on_music_player_stopped)
            self.stacked_widget.addWidget(self.music_player)
        self.stacked_widget.setCurrentWidget(self.music_player)
        self.back_button.setVisible(True)
        self.media_player.pause()  # Pause the menu music
        # Set the music player volume to match the current volume
        self.music_player.set_volume(self.volume_slider.value())

    def on_music_player_started(self):
        self.media_player.pause()  # Ensure menu music is paused when music player starts

    def on_music_player_stopped(self):
        if self.stacked_widget.currentWidget() == self.music_player:
            self.media_player.play()  # Resume menu music if still on music player screen and no music is playing

    def update_volume_slider(self, value):
        self.volume_slider.setValue(value)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())