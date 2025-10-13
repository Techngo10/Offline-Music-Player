import pygame
import random
import os
from tkinter import Tk, filedialog

# Supported audio file extensions
AUDIO_EXTENSIONS = ('.mp3', '.wav', '.flac', '.ogg')

class MusicPlayer:
    def __init__(self, playlist):
        pygame.mixer.init()
        self.playlist = playlist
        self.current_index = 0
        self.is_paused = False
        self.loop = False
        self.shuffle = False

    def play(self, song=None):
        """Play or resume the current song."""
        if not self.playlist:
            print("❌ Playlist is empty.")
            return

        # ✅ If paused, just resume instead of restarting
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            print(f"▶️ Resumed: {os.path.basename(self.playlist[self.current_index])}")
            return

        # Otherwise, load and play a new song
        if song is None:
            song = self.playlist[self.current_index]

        try:
            pygame.mixer.music.load(song)
            pygame.mixer.music.play(-1 if self.loop else 0)
            self.is_paused = False
            print(f"🎵 Now playing: {os.path.basename(song)}")
        except pygame.error as e:
            print(f"⚠️ Could not play {song}: {e}")


    def pause(self):
        
        pygame.mixer.music.pause()
        print(f"⏸️ Paused.")

    def resume(self):
        pygame.mixer.music.unpause()
        print(f"▶️ Resumed: {os.path.basename(self.playlist[self.current_index])}")

    def stop(self):
        pygame.mixer.music.stop()
        print("⏹️ Stopped playback.")

    def next_song(self):
        if not self.playlist:
            return
        if self.shuffle:
            self.current_index = random.randint(0, len(self.playlist)-1)
        else:
            self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play()

    def previous_song(self):
        if not self.playlist:
            return
        if self.shuffle:
            self.current_index = random.randint(0, len(self.playlist)-1)
        else:
            self.current_index = (self.current_index - 1) % len(self.playlist)
        self.play()

    def toggle_loop(self):
        self.loop = not self.loop
        print(f"🔁 Looping is now {'enabled' if self.loop else 'disabled'}.")

    def toggle_shuffle(self):
        self.shuffle = not self.shuffle
        print(f"🔀 Shuffle is now {'enabled' if self.shuffle else 'disabled'}.")

def choose_folder():
    """Open a folder picker and return all songs inside."""
    root = Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title="Select your music folder")
    root.destroy()

    if not folder:
        print("❌ No folder selected.")
        return []

    songs = [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().endswith(AUDIO_EXTENSIONS)
    ]
    if not songs:   
        print("🎧 No audio files found in that folder.")
    else:
        print(f"\n🎶 --- Playlist ({len(songs)} songs) --- 🎶\n")
        for i, song in enumerate(sorted(songs), start=1):
            print(f"{i}. {os.path.basename(song)}")
        print("🎶 ---------------------------------------- 🎶\n")
    return sorted(songs)
