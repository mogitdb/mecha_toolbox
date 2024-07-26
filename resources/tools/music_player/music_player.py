import os
import sys
import random
import json
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QListWidget, QLabel, QFileDialog, QMessageBox, QListWidgetItem)
from PySide6.QtCore import Qt, QUrl, QDir, Signal
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import QSettings

class SongWidget(QWidget):
    play_requested = Signal(str)

    def __init__(self, song_path):
        super().__init__()
        self.song_path = song_path
        layout = QHBoxLayout(self)
        self.play_button = QPushButton("▶")
        self.play_button.setFixedSize(30, 30)
        self.play_button.clicked.connect(self.request_play)
        self.song_label = QLabel(os.path.basename(song_path))
        layout.addWidget(self.play_button)
        layout.addWidget(self.song_label)

    def request_play(self):
        self.play_requested.emit(self.song_path)

class MusicPlayer(QWidget):
    music_started = Signal()
    music_stopped = Signal()

    def __init__(self, parent=None, user_folder=None):
        super().__init__(parent)
        self.user_folder = user_folder
        self.setWindowTitle("Music Player")
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.setup_ui()
        self.current_playlist = []
        self.current_song_index = -1
        self.is_shuffled = False
        self.is_looping = False
        self.check_first_launch()

        self.player.mediaStatusChanged.connect(self.on_media_status_changed)

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Playlist selection
        self.playlist_label = QLabel("Select Playlist:")
        layout.addWidget(self.playlist_label)
        self.playlist_list = QListWidget()
        layout.addWidget(self.playlist_list)
        self.refresh_playlists()

        # Song list
        self.song_list = QListWidget()
        layout.addWidget(self.song_list)

        # Control panel
        control_layout = QHBoxLayout()
        self.play_pause_button = QPushButton("Play")
        self.play_pause_button.clicked.connect(self.play_pause)
        control_layout.addWidget(self.play_pause_button)

        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.previous_song)
        control_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_song)
        control_layout.addWidget(self.next_button)

        self.shuffle_button = QPushButton("Shuffle")
        self.shuffle_button.clicked.connect(self.toggle_shuffle)
        control_layout.addWidget(self.shuffle_button)

        self.loop_button = QPushButton("Loop")
        self.loop_button.clicked.connect(self.toggle_loop)
        control_layout.addWidget(self.loop_button)

        layout.addLayout(control_layout)

        # Now playing label
        self.now_playing_label = QLabel("Now Playing: ")
        layout.addWidget(self.now_playing_label)

    def check_first_launch(self):
        settings_path = os.path.join(self.user_folder, "settings.json")
        settings = {}
        if os.path.exists(settings_path):
            with open(settings_path, "r") as f:
                settings = json.load(f)
        
        if not settings.get("music_player_first_launch", True):
            return

        message = ("Welcome to the Music Player!\n\n"
                "This player will look for playlists in your Music folder.\n"
                "Place your playlist folders in:\n"
                f"{os.path.join(QDir.homePath(), 'Music', 'playlists')}\n\n"
                "Enjoy your tunes!")
        QMessageBox.information(self, "Music Player - First Launch", message)
        
        settings["music_player_first_launch"] = False
        with open(settings_path, "w") as f:
            json.dump(settings, f)

    def refresh_playlists(self):
        playlists_dir = os.path.join(QDir.homePath(), "Music", "playlists")
        if not os.path.exists(playlists_dir):
            os.makedirs(playlists_dir)
        
        self.playlist_list.clear()
        for playlist in os.listdir(playlists_dir):
            self.playlist_list.addItem(playlist)
        
        self.playlist_list.itemClicked.connect(self.load_playlist)

    def load_playlist(self, item):
        # Stop current playback
        self.player.stop()
        self.play_pause_button.setText("Play")
        self.now_playing_label.setText("Now Playing: ")
        self.current_song_index = -1

        playlist_name = item.text()
        playlist_path = os.path.join(QDir.homePath(), "Music", "playlists", playlist_name)
        self.current_playlist = sorted([
            os.path.join(playlist_path, f) 
            for f in os.listdir(playlist_path) 
            if f.endswith(('.mp3', '.wav'))
        ])
        self.update_song_list()

    def update_song_list(self):
        self.song_list.clear()
        for song_path in self.current_playlist:
            item = QListWidgetItem(self.song_list)
            song_widget = SongWidget(song_path)
            song_widget.play_requested.connect(self.play_song_by_path)
            item.setSizeHint(song_widget.sizeHint())
            self.song_list.setItemWidget(item, song_widget)

    def play_song_by_path(self, song_path):
        self.current_song_index = self.current_playlist.index(song_path)
        self.play_current_song()

    def play_pause(self):
        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.play_pause_button.setText("Play")
            self.music_stopped.emit()
        else:
            if self.current_song_index == -1 and self.current_playlist:
                self.current_song_index = 0
            self.play_current_song()

    def play_current_song(self):
        if 0 <= self.current_song_index < len(self.current_playlist):
            self.player.setSource(QUrl.fromLocalFile(self.current_playlist[self.current_song_index]))
            self.player.play()
            self.play_pause_button.setText("Pause")
            self.now_playing_label.setText(f"Now Playing: {os.path.basename(self.current_playlist[self.current_song_index])}")
            self.music_started.emit()

    def set_volume(self, value):
        self.audio_output.setVolume(value / 100.0)

    def next_song(self):
        if self.current_playlist:
            self.current_song_index = (self.current_song_index + 1) % len(self.current_playlist)
            self.play_current_song()

    def previous_song(self):
        if self.current_playlist:
            self.current_song_index = (self.current_song_index - 1) % len(self.current_playlist)
            self.play_current_song()

    def toggle_shuffle(self):
        self.is_shuffled = not self.is_shuffled
        if self.is_shuffled:
            random.shuffle(self.current_playlist)
            self.shuffle_button.setStyleSheet("background-color: lightblue;")
        else:
            self.current_playlist.sort()
            self.shuffle_button.setStyleSheet("")
        self.update_song_list()

    def toggle_loop(self):
        self.is_looping = not self.is_looping
        if self.is_looping:
            self.loop_button.setStyleSheet("background-color: lightblue;")
        else:
            self.loop_button.setStyleSheet("")

    def on_media_status_changed(self, status):
        if status == QMediaPlayer.EndOfMedia:
            if self.is_looping:
                self.player.setPosition(0)
                self.player.play()
            else:
                self.next_song()

    def stop_playback(self):
        self.player.stop()
        self.play_pause_button.setText("Play")
        self.music_stopped.emit()

def show_music_player(parent, user_folder):
    return MusicPlayer(parent, user_folder)