import pygame
import random
import os
from tkinter import Tk, filedialog

# Supported audio file extensions
AUDIO_EXTENSIONS = ('.mp3', '.wav', '.flac', '.ogg')

class MusicPlayer:
    def __init__(self, playlist):
        pygame.mixer.init()
        pygame.display.init()
        pygame.display.set_mode((1, 1))

        pygame.mixer.music.set_endevent(pygame.USEREVENT)  # 🔔 Set custom event when a song ends
        self.playlist = playlist
        self.current_index = 0
        self.loop = False
        self.shuffle = False

    def play(self, song=None):
        """Play or resume a song."""
        if not self.playlist:
            print("❌ Playlist is empty.")
            return

        if song is None:
            song = self.playlist[self.current_index]

        try:
            pygame.mixer.music.load(song)
            pygame.mixer.music.play(-1 if self.loop else 0)
            print(f"🎵 Now playing: {os.path.basename(song)}")
        except pygame.error as e:
            print(f"⚠️ Could not play {song}: {e}")

    def play_by_number(self, number):
        """Play a specific song by its playlist number."""
        if number < 1 or number > len(self.playlist):
            print("⚠️ No song available for that number.")
            return
        self.current_index = number - 1
        self.play()

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
            self.current_index = random.randint(0, len(self.playlist) - 1)
        else:
            self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play()

    def previous_song(self):
        if not self.playlist:
            return
        if self.shuffle:
            self.current_index = random.randint(0, len(self.playlist) - 1)
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
        print(f"\n🎶 --- Playlist ({len(songs)} songs) ---\n")
        for i, song in enumerate(sorted(songs), start=1):
            print(f"{i}. {os.path.basename(song)}")
        print("----------------\n")

    return sorted(songs)


if __name__ == "__main__":
    playlist = choose_folder()
    player = MusicPlayer(playlist)

    print("✅ Type commands like: play 1 | pause | resume | stop | next | prev | shuffle | loop | quit")

    running = True
    while running:
        # 🧠 Check if a song finished
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT:
                print("➡️  Song finished, playing next...")
                player.next_song()

        command = input("\nEnter command: ").strip().lower()

        if command.startswith("play "):
            try:
                num = int(command.split()[1])
                player.play_by_number(num)
            except ValueError:
                print("⚠️ Please enter a valid number after 'play'.")
        elif command == "play":
            player.play()
        elif command == "pause":
            player.pause()
        elif command == "resume":
            player.resume()
        elif command == "stop":
            player.stop()
        elif command == "next":
            player.next_song()
        elif command == "prev":
            player.previous_song()
        elif command == "loop":
            player.toggle_loop()
        elif command == "shuffle":
            player.toggle_shuffle()
        elif command == "quit":
            player.stop()
            print("👋 Goodbye!")
            running = False
        else:
            print("Unknown command.")
