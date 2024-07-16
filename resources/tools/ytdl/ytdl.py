import subprocess
import sys
import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QLineEdit, QProgressBar, QMessageBox)
from PySide6.QtCore import Qt, Signal, QThread

class DownloadThread(QThread):
    update_progress = Signal(str)
    download_complete = Signal()

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        # Use the user's Music folder
        music_folder = os.path.join(os.path.expanduser("~"), "Music")
        mp3_folder = os.path.join(music_folder, "yt_mp3")
        mp4_folder = os.path.join(music_folder, "yt_mp4")

        # Create folders if they don't exist
        for folder in [mp3_folder, mp4_folder]:
            if not os.path.exists(folder):
                os.makedirs(folder)

        video_command = [
            'yt-dlp',
            '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            '--merge-output-format', 'mp4',
            '-o', os.path.join(mp4_folder, '%(title)s.%(ext)s'),
            self.url
        ]
        audio_command = [
            'yt-dlp',
            '-x', '--audio-format', 'mp3',
            '-o', os.path.join(mp3_folder, '%(title)s.%(ext)s'),
            self.url
        ]

        try:
            subprocess.run(video_command, check=True)
            subprocess.run(audio_command, check=True)
            self.download_complete.emit()
        except subprocess.CalledProcessError as e:
            self.update_progress.emit(f"An error occurred: {str(e)}")

class YouTubeDownloader(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("YouTube Downloader")
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.url_entry = QLineEdit()
        self.url_entry.setPlaceholderText("Enter YouTube URL")
        layout.addWidget(self.url_entry)

        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.start_download)
        layout.addWidget(self.download_button)

        self.progress_label = QLabel("Ready to download")
        layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

    def start_download(self):
        url = self.url_entry.text()
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a YouTube URL")
            return

        self.download_thread = DownloadThread(url)
        self.download_thread.update_progress.connect(self.update_progress_label)
        self.download_thread.download_complete.connect(self.download_finished)
        
        self.download_thread.start()
        self.progress_bar.setVisible(True)
        self.download_button.setEnabled(False)
        self.progress_label.setText("Download in Progress...")

    def update_progress_label(self, message):
        self.progress_label.setText(message)

    def download_finished(self):
        self.progress_bar.setVisible(False)
        self.progress_label.setText("Download Complete")
        self.download_button.setEnabled(True)
        
        # Show the download locations
        music_folder = os.path.expanduser("~/Music")
        QMessageBox.information(self, "Download Complete", 
                                f"Files have been saved to:\n\n"
                                f"MP3: {os.path.join(music_folder, 'yt_mp3')}\n"
                                f"MP4: {os.path.join(music_folder, 'yt_mp4')}")

def show_youtube_downloader(parent):
    dialog = YouTubeDownloader(parent)
    dialog.exec()

def is_yt_dlp_installed():
    try:
        subprocess.run(['yt-dlp', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        return False

def install_yt_dlp():
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'yt-dlp'])

# Check and install yt-dlp if not installed
if not is_yt_dlp_installed():
    print("Installing yt-dlp...")
    install_yt_dlp()