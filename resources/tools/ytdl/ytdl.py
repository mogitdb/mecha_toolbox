import subprocess
import sys
import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QLineEdit, QProgressBar, QMessageBox,
                               QCheckBox, QFileDialog)
from PySide6.QtCore import Qt, Signal, QThread

class DownloadThread(QThread):
    update_progress = Signal(str)
    download_complete = Signal(str)

    def __init__(self, url, download_video, download_audio, output_folder):
        super().__init__()
        self.url = url
        self.download_video = download_video
        self.download_audio = download_audio
        self.output_folder = output_folder

    def run(self):
        try:
            if self.download_video:
                self.download_highest_quality_video()
            if self.download_audio:
                self.download_highest_quality_audio()
            self.download_complete.emit(self.output_folder)
        except subprocess.CalledProcessError as e:
            self.update_progress.emit(f"An error occurred: {str(e)}")

    def download_highest_quality_video(self):
        command = [
            'yt-dlp',
            '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            '--merge-output-format', 'mp4',
            '-o', os.path.join(self.output_folder, '%(title)s.%(ext)s'),
            self.url
        ]
        self.update_progress.emit("Downloading video...")
        subprocess.run(command, check=True)

    def download_highest_quality_audio(self):
        command = [
            'yt-dlp',
            '-f', 'bestaudio',
            '--extract-audio',
            '--audio-format', 'mp3',
            '--audio-quality', '0',  # 0 is the best quality
            '-o', os.path.join(self.output_folder, '%(title)s.%(ext)s'),
            self.url
        ]
        self.update_progress.emit("Downloading audio...")
        subprocess.run(command, check=True)

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

        self.video_checkbox = QCheckBox("Download Video")
        self.video_checkbox.setChecked(True)
        layout.addWidget(self.video_checkbox)

        self.audio_checkbox = QCheckBox("Download Audio")
        self.audio_checkbox.setChecked(True)
        layout.addWidget(self.audio_checkbox)

        self.output_folder = os.path.expanduser("~/Downloads")
        self.output_folder_label = QLabel(f"Output folder: {self.output_folder}")
        layout.addWidget(self.output_folder_label)

        self.change_folder_button = QPushButton("Change Output Folder")
        self.change_folder_button.clicked.connect(self.change_output_folder)
        layout.addWidget(self.change_folder_button)

        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.start_download)
        layout.addWidget(self.download_button)

        self.progress_label = QLabel("Ready to download")
        layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.open_folder_button = QPushButton("Open Output Folder")
        self.open_folder_button.clicked.connect(self.open_output_folder)
        self.open_folder_button.setVisible(False)
        layout.addWidget(self.open_folder_button)

    def change_output_folder(self):
        new_folder = QFileDialog.getExistingDirectory(self, "Select Output Folder", self.output_folder)
        if new_folder:
            self.output_folder = new_folder
            self.output_folder_label.setText(f"Output folder: {self.output_folder}")

    def start_download(self):
        url = self.url_entry.text()
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a YouTube URL")
            return

        if not self.video_checkbox.isChecked() and not self.audio_checkbox.isChecked():
            QMessageBox.warning(self, "Error", "Please select at least one download option")
            return

        self.download_thread = DownloadThread(
            url, 
            self.video_checkbox.isChecked(), 
            self.audio_checkbox.isChecked(),
            self.output_folder
        )
        self.download_thread.update_progress.connect(self.update_progress_label)
        self.download_thread.download_complete.connect(self.download_finished)
        
        self.download_thread.start()
        self.progress_bar.setVisible(True)
        self.download_button.setEnabled(False)
        self.progress_label.setText("Download in Progress...")

    def update_progress_label(self, message):
        self.progress_label.setText(message)

    def download_finished(self, output_folder):
        self.progress_bar.setVisible(False)
        self.progress_label.setText("Download Complete")
        self.download_button.setEnabled(True)
        self.open_folder_button.setVisible(True)
        
        QMessageBox.information(self, "Download Complete", 
                                f"Files have been saved to:\n\n{output_folder}")

    def open_output_folder(self):
        if sys.platform.startswith('win'):
            os.startfile(self.output_folder)
        elif sys.platform.startswith('darwin'):
            subprocess.run(['open', self.output_folder])
        else:
            subprocess.run(['xdg-open', self.output_folder])

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