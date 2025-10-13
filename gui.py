import tkinter as tk
from tkinter import ttk
from music_player import MusicPlayer, choose_folder
import os

class MusicApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Offline Music Player")
        self.root.geometry("900x500")
        self.root.configure(bg="#121212")

        # --- Initialize player and states ---
        self.playlist = choose_folder()
        self.player = MusicPlayer(self.playlist)
        self.is_playing = False
        self.scroll_job = None  # track marquee animation job

        # --- Styles ---
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background="#121212", foreground="white", font=("Segoe UI", 12))
        style.configure("TButton", background="#1DB954", foreground="white", font=("Segoe UI", 10, "bold"))
        style.map("TButton", background=[("active", "#1ED760")])

        self.build_ui()

    def build_ui(self):
        # --- Top Bar ---
        top_bar = tk.Frame(self.root, bg="#121212", height=50, pady=10)
        top_bar.pack(side="top", fill="x")
        ttk.Button(top_bar, text="Home").grid(row=0, column=0, padx=10)
        ttk.Button(top_bar, text="Download").grid(row=0, column=1, padx=10)

        # --- Main Area Placeholder ---
        main_frame = tk.Frame(self.root, bg="#535353")
        main_frame.pack(fill="both", expand=True)
        ttk.Label(main_frame, text="(Playlist view coming soon)", foreground="#888", background="#535353").pack(pady=150)

        # --- Bottom Bar ---
        bottom_bar = tk.Frame(self.root, bg="#121212", height=100)
        bottom_bar.pack(side="bottom", fill="x")

        bottom_bar.columnconfigure(0, weight=1)
        bottom_bar.columnconfigure(1, weight=1)
        bottom_bar.columnconfigure(2, weight=1)

        # --- Left: Song Info ---
        self.song_info_frame = tk.Frame(bottom_bar, bg="#181818", width=250, height=60)
        self.song_info_frame.grid(row=0, column=0, sticky="w", padx=30, pady=10)
        self.song_info_frame.pack_propagate(False)

        self.song_title = ttk.Label(
            self.song_info_frame,
            text="No song playing",
            font=("Segoe UI", 11, "bold"),
            anchor="w"
        )
        self.song_title.pack(fill="x")

        self.song_artist = ttk.Label(
            self.song_info_frame,
            text="",
            font=("Segoe UI", 9),
            foreground="#B3B3B3",
            anchor="w"
        )
        self.song_artist.pack(fill="x")

        # --- Center: Playback Controls ---
        controls_frame = tk.Frame(bottom_bar, bg="#181818")
        controls_frame.grid(row=0, column=1)

        self.prev_button = ttk.Button(controls_frame, text="⏮", command=self.previous_song)
        self.play_button = ttk.Button(controls_frame, text="▶", command=self.toggle_play)
        self.next_button = ttk.Button(controls_frame, text="⏭", command=self.next_song)

        self.prev_button.grid(row=0, column=0, padx=10)
        self.play_button.grid(row=0, column=1, padx=10)
        self.next_button.grid(row=0, column=2, padx=10)

        # --- Right: Volume ---
        volume_frame = tk.Frame(bottom_bar, bg="#181818")
        volume_frame.grid(row=0, column=2, sticky="e", padx=30)
        ttk.Label(volume_frame, text="🔊", background="#181818").pack(side="left", padx=5)
        volume_slider = ttk.Scale(volume_frame, from_=0, to=100, orient="horizontal", length=120)
        volume_slider.set(70)
        volume_slider.pack(side="left")

    # --- Player Controls ---
    def toggle_play(self):
        if not self.playlist:
            print("❌ No songs loaded.")
            return

        # If paused, resume
        if self.player.is_paused:
            self.player.resume()
            self.is_playing = True
            self.play_button.config(text="⏸")
            return

        # If not playing, start playing
        if not self.is_playing:
            self.player.play()
            self.is_playing = True
            self.play_button.config(text="⏸")
            self.update_song_info()
        else:
            # Otherwise pause
            self.player.pause()
            self.is_playing = False
            self.play_button.config(text="▶")

    def next_song(self):
        self.player.next_song()
        self.is_playing = True
        self.play_button.config(text="⏸")
        self.update_song_info()

    def previous_song(self):
        self.player.previous_song()
        self.is_playing = True
        self.play_button.config(text="⏸")
        self.update_song_info()

    # --- Info Update + Marquee ---
    def update_song_info(self):
        """Update the display with the current song and reset marquee."""
        song_path = self.player.playlist[self.player.current_index]
        song_name = os.path.basename(song_path)
        song_name, _ = os.path.splitext(song_name)
        self.song_title.config(text=song_name)
        self.song_artist.config(text="Unknown Artist")

        if self.scroll_job:
            self.root.after_cancel(self.scroll_job)
            self.scroll_job = None

        if len(song_name) > 25:
            self.scroll_text(song_name + "   ", 0)

    def scroll_text(self, text, pos):
        """Smooth scrolling marquee effect."""
        cropped = text[pos:pos+25]
        if len(cropped) < 25:
            cropped += text[:25 - len(cropped)]
        self.song_title.config(text=cropped)
        next_pos = (pos + 1) % len(text)
        self.scroll_job = self.root.after(200, lambda: self.scroll_text(text, next_pos))

# --- Run App ---
if __name__ == "__main__":
    root = tk.Tk()
    app = MusicApp(root)
    root.mainloop()
