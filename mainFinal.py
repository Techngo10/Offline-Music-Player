# gui_combined.py
import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import subprocess
import sys
from LoginApp import show_login
import threading


from Classes import User, Playlist
from musicPlayer import MusicPlayer

DB_FILE = "musicApp.db"
# testing: assume user 1 is logged in (you can change as needed)
curr_user = User(DB_FILE, 1)
DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "downloads")

# Ensure the folder exists
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)


# -------------------------------
# 🏠 MAIN APPLICATION CONTROLLER
# -------------------------------
class MusicApp(tk.Tk):
    def __init__(self, curr_user):
        super().__init__()
        self.curr_user = curr_user
        self.title("Offline Music Player")
        self.attributes('-fullscreen', True)
        self.configure(bg="#121212")

        container = tk.Frame(self, bg="#121212")
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (MainPage, DownloadPage, AccountPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(MainPage)

    def show_frame(self, page_class):
        frame = self.frames[page_class]
        frame.tkraise()


# -------------------------------
# 🎵 MAIN PAGE (PLAYER / PLAYLIST)
# -------------------------------
class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#121212")
        self.controller = controller
        self.curr_user = controller.curr_user 
        # Music player instance (start empty)
        self.player = MusicPlayer([])

        # current selected playlist info
        self.current_playlist_id = None
        self.playlist_ids = []
        self.current_playlist_paths = []

        # layout configuration
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Styles (simple)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background="#181818", foreground="white")
        style.configure("TButton", background="#1DB954", foreground="white")

        # Top bar (with navigation)
        top_bar = tk.Frame(self, bg="#181818", height=64)
        top_bar.grid(row=0, column=0, sticky="nsew")
        top_bar.grid_propagate(False)
        tk.Label(top_bar, text="🎵 Offline Music Player", fg="white", bg="#181818",
                 font=("Segoe UI", 12, "bold")).pack(side="left", padx=12)
        ttk.Button(top_bar, text="Home", command=lambda: controller.show_frame(MainPage)).pack(side="left", padx=6, pady=10)
        # ttk.Button(top_bar, text="Download", command=lambda: controller.show_frame(DownloadPage)).pack(side="left", padx=6)
        ttk.Button(top_bar, text="Account", command=self.open_user_profile).pack(side="left", padx=6)

        # Main content area (3 columns)
        main_frame = tk.Frame(self, bg="#121212")
        main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.columnconfigure(2, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Left: playlist listbox
        playlist_frame = tk.Frame(main_frame, bg="#181818")
        playlist_frame.grid(row=0, column=0, sticky="nsew", padx=6)
        tk.Label(playlist_frame, text="Playlists", fg="white", bg="#181818", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=8, pady=6)
        self.playlist_box = tk.Listbox(playlist_frame, bg="#202020", fg="white", selectbackground="#404040")
        self.playlist_box.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.playlist_box.bind("<<ListboxSelect>>", self.show_playlist_songs)

        # Middle: songs listbox
        songs_frame = tk.Frame(main_frame, bg="#181818")
        songs_frame.grid(row=0, column=1, sticky="nsew", padx=6)
        tk.Label(songs_frame, text="Songs", fg="white", bg="#181818", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=8, pady=6)
        self.songs_box = tk.Listbox(songs_frame, bg="#202020", fg="white", selectbackground="#404040")
        self.songs_box.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        # play a singled-clicked song (optional: double-click)
        self.songs_box.bind("<Double-Button-1>", self.play_selected_song)

        # Right: playlist controls
        controls_frame = tk.Frame(main_frame, bg="#181818")
        controls_frame.grid(row=0, column=2, sticky="nsew", padx=6)
        tk.Label(controls_frame, text="Playlist Controls", fg="white", bg="#181818", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=8, pady=6)

        ttk.Button(controls_frame, text="+ Create Playlist", command=self.create_playlist).pack(fill="x", padx=8, pady=4)
        ttk.Button(controls_frame, text="✏ Rename Playlist", command=self.rename_playlist_popup).pack(fill="x", padx=8, pady=4)
        ttk.Button(controls_frame, text="🗑 Delete Playlist", command=self.delete_playlist).pack(fill="x", padx=8, pady=4)
        ttk.Button(controls_frame, text="▶ Play Playlist", command=self.play_playlist).pack(fill="x", padx=8, pady=8)
        ttk.Separator(controls_frame, orient="horizontal").pack(fill="x", padx=8, pady=8)
        # ttk.Button(controls_frame, text="+ Add Song (pick file)", command=self.add_song_file_to_db).pack(fill="x", padx=8, pady=4)
        ttk.Button(
            controls_frame,
            text="Download song",
            command=self.run_add_song_script
        ).pack(fill="x", padx=8, pady=4)
        # ttk.Button(controls_frame, text="❌ Remove Song", command=self.remove_song).pack(fill="x", padx=8, pady=4)
        ttk.Button(controls_frame, text="📷 Add Cover", command=self.add_playlist_cover).pack(fill="x", padx=8, pady=4)
        ttk.Button(controls_frame, text="🖼 Remove Cover", command=self.delete_playlist_cover).pack(fill="x", padx=8, pady=4)
 

        
        # cover thumbnail
        self.cover_label = tk.Label(controls_frame, text="No cover", bg="#181818", fg="white")
        self.cover_label.pack(pady=8)

        # Bottom player bar
        bottom_bar = tk.Frame(self, bg="#181818", height=84)
        bottom_bar.grid(row=2, column=0, sticky="nsew")
        bottom_bar.grid_propagate(False)
        bottom_bar.columnconfigure(0, weight=1)
        bottom_bar.columnconfigure(1, weight=1)
        bottom_bar.columnconfigure(2, weight=1)

        # song info
        song_info = tk.Frame(bottom_bar, bg="#181818")
        song_info.grid(row=0, column=0, sticky="w", padx=16)
        self.song_title_label = tk.Label(song_info, text="Song Title", fg="white", bg="#181818", font=("Segoe UI", 10, "bold"))
        self.song_title_label.pack(anchor="w")
        self.song_artist_label = tk.Label(song_info, text="Artist Name", fg="#b3b3b3", bg="#181818", font=("Segoe UI", 9))
        self.song_artist_label.pack(anchor="w")

        # playback controls
        player_controls = tk.Frame(bottom_bar, bg="#181818")
        player_controls.grid(row=0, column=1)
        ttk.Button(player_controls, text="⏮", command=self.previous_song).grid(row=0, column=0, padx=8)
        ttk.Button(player_controls, text="▶", command=self.play_button_action).grid(row=0, column=1, padx=8)
        ttk.Button(player_controls, text="⏭", command=self.next_song).grid(row=0, column=2, padx=8)
        ttk.Button(player_controls, text="⏸", command=self.pause_song).grid(row=0, column=3, padx=8)


        # volume placeholder
        # volume_frame = tk.Frame(bottom_bar, bg="#181818")
        # volume_frame.grid(row=0, column=2, sticky="e", padx=16)
        # tk.Label(volume_frame, text="🔊", fg="white", bg="#181818").pack(side="left")
        # ttk.Scale(volume_frame, from_=0, to=100, orient="horizontal", length=120).pack(side="left", padx=8)

        # initial population
        self.disp_playlists()

    # -------------------- Playlist UI / DB Functions -------------------- #
    def on_volume_change(self, val):
        volume = float(val) / 100  # convert 0-100 to 0.0-1.0
        self.player.set_volume(volume)
    
    def pause_song(self):
        if self.player.playlist:
            self.player.pause()  
        else:
            messagebox.showinfo("Info", "No song is currently playing.")

    def play_button_action(self):
        song_sel = self.songs_box.curselection()
        playlist_sel = self.playlist_box.curselection()

        if song_sel:
            # play the selected song
            self.play_selected_song()
        elif playlist_sel:
            # play the selected playlist
            self.play_playlist()
        else:
            # resume/pause current playback
            if self.player.playlist:
                self.player.toggle_play()
            else:
                messagebox.showinfo("Info", "Select a song or playlist to play.")

    
    def run_add_song_script(self):
        script_path = os.path.join(os.path.dirname(__file__), "add_song.py")
        if os.path.exists(script_path):
            # Run in a separate process
            subprocess.Popen([sys.executable, script_path])
        else:
            messagebox.showerror("Error", "add_song.py not found!")

    def open_user_profile(self):
        # Make sure it runs with the same Python interpreter
        subprocess.Popen([sys.executable, "user_profile.py"])

    def disp_playlists(self):
        self.playlist_box.delete(0, tk.END)
        self.playlist_ids = []
        try:
            playlists = curr_user.viewPlaylists()
        except Exception:
            playlists = []
        for pid, name in playlists:
            self.playlist_box.insert(tk.END, name)
            self.playlist_ids.append(pid)
        # Auto-select first playlist after widget fully rendered
        if self.playlist_ids:
            self.playlist_box.selection_set(0)
            # Schedule the update to happen after Tkinter mainloop starts
            self.after(100, self.show_playlist_songs)


    def create_playlist(self):
        """
        Creates a new empty playlist for the current user.
        """
        try:
            # Pass None as firstSong to create an empty playlist
            new_id = curr_user.createNew(None)
            messagebox.showinfo("Success", f"Created empty playlist #{new_id}")
            self.disp_playlists()
        except Exception as e:
            messagebox.showerror("Error", f"Could not create playlist:\n{str(e)}")


    def rename_playlist_popup(self):
        selection = self.playlist_box.curselection()
        if not selection:
            messagebox.showwarning("Oops", "Select a playlist first")
            return
        idx = selection[0]
        self.current_playlist_id = self.playlist_ids[idx]

        popup = tk.Toplevel(self)
        popup.title("Rename Playlist")
        tk.Label(popup, text="New Name:").pack(padx=10, pady=5)
        name_entry = tk.Entry(popup)
        name_entry.pack(padx=10, pady=5)

        def rename_action():
            new_name = name_entry.get().strip()
            if new_name:
                pl = Playlist(DB_FILE, self.current_playlist_id)
                pl.changePlaylistName(new_name)
                messagebox.showinfo("Renamed", f"Playlist renamed to {new_name}")
                self.disp_playlists()
                popup.destroy()

        ttk.Button(popup, text="Rename", command=rename_action).pack(pady=6)

    def delete_playlist(self):
        selection = self.playlist_box.curselection()
        if not selection:
            messagebox.showwarning("Oops", "Select a playlist first")
            return
        idx = selection[0]
        self.current_playlist_id = self.playlist_ids[idx]
        pl = Playlist(DB_FILE, self.current_playlist_id)
        pl.deletePlaylist()
        messagebox.showinfo("Deleted", "Playlist deleted.")
        self.disp_playlists()
        self.songs_box.delete(0, tk.END)
        self.cover_label.config(image="", text="No cover")

    def show_playlist_songs(self, event=None):
        selection = self.playlist_box.curselection()
        if not selection:
            return
        idx = selection[0]
        self.current_playlist_id = self.playlist_ids[idx]
        pl = Playlist(DB_FILE, self.current_playlist_id)

        # get songs with optional file_path
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.song_id, s.song_name, s.artist_name, s.album_name, s.length, 
                   COALESCE(s.file_path, '') as file_path
            FROM playlist_songs ps
            JOIN songsDownloaded s ON ps.song_id = s.song_id
            WHERE ps.playlist_id = ?
        """, (self.current_playlist_id,))
        songs = cursor.fetchall()
        conn.close()

        self.songs_box.delete(0, tk.END)
        self.current_playlist_paths = []
        if songs:
            for song in songs:
                song_id, song_name, artist, album, length, file_path = song
                display = f"{song_name} - {artist if artist else 'Unknown'}"
                self.songs_box.insert(tk.END, display)
                # store file_path if available
                if file_path:
                    # convert to absolute path if stored relative
                    file_path = os.path.abspath(file_path) if not os.path.isabs(file_path) else file_path
                    self.current_playlist_paths.append(file_path)
        else:
            self.songs_box.insert(tk.END, "No songs in this playlist")

        # show cover if present
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT cover_photo FROM playlist WHERE playlist_id = ?", (self.current_playlist_id,))
        row = cursor.fetchone()
        conn.close()
        cover_path = row[0] if row else None
        if cover_path and os.path.exists(cover_path):
            img = Image.open(cover_path).resize((140, 140))
            tk_img = ImageTk.PhotoImage(img)
            self.cover_label.config(image=tk_img, text="")
            self.cover_label.image = tk_img
        else:
            self.cover_label.config(image="", text="No cover")

    def play_selected_song(self, event=None):
        sel = self.songs_box.curselection()
        if not sel:
            return
        idx = sel[0]

        if idx >= len(self.current_playlist_paths):
            messagebox.showwarning("Missing file", "File path not found for this song.")
            return

        song_path = self.current_playlist_paths[idx]
        if not os.path.exists(song_path):
            messagebox.showwarning("Missing file", "File missing on disk:\n" + song_path)
            return

        if not self.current_playlist_paths:
            messagebox.showwarning("Empty", "No songs in the playlist.")
            return

        self.player.playlist = self.current_playlist_paths
        self.player.current_index = idx
        self.player.play()
        self.update_song_info(self.current_playlist_paths[idx])

        self.update_song_info(song_path)


    def play_playlist(self):
        print("Current playlist ID:", self.current_playlist_id)
        if not self.current_playlist_id:
            messagebox.showwarning("Oops", "Select a playlist first!")
            return

        # query file paths for playlist
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.file_path
            FROM playlist_songs ps
            JOIN songsDownloaded s ON ps.song_id = s.song_id
            WHERE ps.playlist_id = ?
        """, (self.current_playlist_id,))
        files = [row[0] for row in cursor.fetchall() if row[0]]
        conn.close()

        if not files:
            messagebox.showwarning("Empty", "No valid songs with paths found for this playlist.")
            return

        # convert to absolute paths where necessary
        files = [os.path.abspath(f) if not os.path.isabs(f) else f for f in files]

        self.player.playlist = files
        self.player.current_index = 0
        self.player.play()

        # update UI for currently playing file
        self.update_song_info(files[0])

        # optional popup
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT playlist_name FROM playlist WHERE playlist_id = ?", (self.current_playlist_id,))
        row = c.fetchone()
        conn.close()
        pl_name = row[0] if row else "Playlist"
        messagebox.showinfo("Now Playing", f"Playing playlist: {pl_name}")

    def remove_song(self):
        selection = self.songs_box.curselection()
        if not selection:
            messagebox.showwarning("Oops", "Select a song first")
            return
        idx = selection[0]
        song_text = self.songs_box.get(idx)
        song_name = song_text.split(" - ")[0]
        # find song_id
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT song_id FROM songsDownloaded WHERE song_name = ?", (song_name,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            messagebox.showwarning("Error", "Could not locate song to remove.")
            return
        song_id = row[0]
        pl = Playlist(DB_FILE, self.current_playlist_id)
        pl.removeSong(song_id)
        self.show_playlist_songs()
        messagebox.showinfo("Removed", f"Removed {song_name} from playlist")

    def add_song_file_to_db(self):
        # pick a local audio file and add it to songsDownloaded and optionally to current playlist
        filetypes = [("Audio files", "*.mp3 *.wav *.flac *.ogg"), ("All files", "*.*")]
        file_path = filedialog.askopenfilename(title="Select audio file", filetypes=filetypes)
        if not file_path:
            return
        # attempt to store metadata minimally
        song_name = os.path.splitext(os.path.basename(file_path))[0]
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""
            INSERT INTO songsDownloaded (song_name, artist_name, file_path)
            VALUES (?, ?, ?)
        """, (song_name, None, file_path))
        song_id = c.lastrowid
        conn.commit()
        conn.close()
        messagebox.showinfo("Added", f"Added {song_name} to downloaded songs (id {song_id}).")

    def add_playlist_cover(self):
        if not self.current_playlist_id:
            messagebox.showwarning("Oops", "Select a playlist first")
            return
        file_path = filedialog.askopenfilename(
            title="Select Cover Image",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.gif")]
        )
        if not file_path:
            return
        pl = Playlist(DB_FILE, self.current_playlist_id)
        pl.uploadCover(file_path)
        self.show_playlist_songs()
        messagebox.showinfo("Success", "Cover image added!")

    def delete_playlist_cover(self):
        if not self.current_playlist_id:
            messagebox.showwarning("Oops", "Select a playlist first")
            return
        pl = Playlist(DB_FILE, self.current_playlist_id)
        pl.removeCover()
        self.show_playlist_songs()
        messagebox.showinfo("Success", "Cover image removed!")

    # -------------------- Player UI helpers -------------------- #
    def update_song_info(self, song_path):
        if not song_path or not os.path.exists(song_path):
            self.song_title_label.config(text="Song Title")
            self.song_artist_label.config(text="Artist Name")
            return
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT song_name, artist_name FROM songsDownloaded WHERE file_path = ?", (song_path,))
        row = cursor.fetchone()
        conn.close()
        if row:
            song_name, artist = row
            self.song_title_label.config(text=song_name)
            self.song_artist_label.config(text=artist if artist else "Unknown Artist")
        else:
            self.song_title_label.config(text=os.path.basename(song_path))
            self.song_artist_label.config(text="Unknown Artist")

    def next_song(self):
        self.player.next_song()
        if self.player.playlist:
            current_file = self.player.playlist[self.player.current_index]
            self.update_song_info(current_file)

    def previous_song(self):
        self.player.previous_song()
        if self.player.playlist:
            current_file = self.player.playlist[self.player.current_index]
            self.update_song_info(current_file)


# -------------------------------
# ⬇️ DOWNLOAD PAGE (YouTube + DB + Playlist)
# -------------------------------
class DownloadPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#121212")
        self.controller = controller

        # Top navigation
        top_bar = tk.Frame(self, bg="#181818", height=54)
        top_bar.pack(side="top", fill="x")
        ttk.Button(top_bar, text="Home", command=lambda: controller.show_frame(MainPage)).pack(side="left", padx=8, pady=8)
        ttk.Button(top_bar, text="Account", command=lambda: controller.show_frame(AccountPage)).pack(side="left", padx=8, pady=8)

        # Body: 3-column layout
        body = tk.Frame(self, bg="#121212")
        body.pack(fill="both", expand=True, padx=12, pady=12)
        for i in range(3):
            body.columnconfigure(i, weight=1)

        # ---------------- Column 1: YouTube Download + Folder ----------------
        col1 = tk.Frame(body, bg="#181818")
        col1.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        tk.Label(col1, text="YouTube Downloader", fg="white", bg="#181818",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=8, pady=6)

        ttk.Button(col1, text="Select Download Folder", command=self.select_download_folder).pack(fill="x", padx=8, pady=4)
        ttk.Label(col1, text="Video URL:").pack(anchor="w", padx=8, pady=(8,0))
        self.yt_url_entry = tk.Entry(col1)
        self.yt_url_entry.pack(fill="x", padx=8, pady=4)
        ttk.Button(col1, text="Download Audio", command=self.download_youtube_audio).pack(fill="x", padx=8, pady=6)

        # ---------------- Column 2: Downloaded Songs ----------------
        col2 = tk.Frame(body, bg="#181818")
        col2.grid(row=0, column=1, sticky="nsew", padx=6, pady=6)
        tk.Label(col2, text="Downloaded Songs", fg="white", bg="#181818",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=8, pady=6)
        self.downloads_listbox = tk.Listbox(col2, bg="#202020", fg="white")
        self.downloads_listbox.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        ttk.Button(col2, text="Refresh", command=self.populate_downloads).pack(pady=6)

        # ---------------- Column 3: Add to Playlist ----------------
        col3 = tk.Frame(body, bg="#181818")
        col3.grid(row=0, column=2, sticky="nsew", padx=6, pady=6)
        tk.Label(col3, text="Add to Playlist", fg="white", bg="#181818",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=8, pady=6)
        self.playlist_combo = ttk.Combobox(col3, state="readonly")
        self.playlist_combo.pack(fill="x", padx=8, pady=6)
        ttk.Button(col3, text="Add Selected Song to Playlist", command=self.add_selected_to_playlist).pack(padx=8, pady=6)

        self.populate_playlists()
        self.populate_downloads()

    # ------------------ Folder selection ------------------
    def select_download_folder(self):
        folder = filedialog.askdirectory(title="Select download folder")
        if folder:
            curr_user.download_folder = folder
            messagebox.showinfo("Folder Selected", f"Downloads will go to:\n{folder}")

    # ------------------ YouTube download ------------------
    def download_youtube_audio(self):
        try:
            import yt_dlp
        except ImportError:
            messagebox.showerror("Missing Library", "yt_dlp module is required. Install via pip.")
            return

        url = self.yt_url_entry.get().strip()
        if not url:
            messagebox.showwarning("No URL", "Please enter a YouTube video URL.")
            return

        # Ensure user download folder exists
        user_folder = os.path.join(DOWNLOAD_DIR, curr_user.username)
        os.makedirs(user_folder, exist_ok=True)

        def download_thread():
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": os.path.join(user_folder, "%(title)s.%(ext)s"),
                "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
                "final_ext": "mp3",
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,
            }
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                # Find the newest downloaded file
                downloaded_files = [
                    os.path.join(user_folder, f) for f in os.listdir(user_folder)
                    if os.path.isfile(os.path.join(user_folder, f))
                ]
                latest_file = max(downloaded_files, key=os.path.getctime)
                latest_file_abs = os.path.abspath(latest_file)

                # Insert into songsDownloaded table
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                song_name = os.path.splitext(os.path.basename(latest_file_abs))[0]
                c.execute("""
                    INSERT INTO songsDownloaded (song_name, artist_name, file_path)
                    VALUES (?, ?, ?)
                """, (song_name, None, latest_file_abs))
                conn.commit()
                conn.close()

                messagebox.showinfo("Download Complete", f"Audio downloaded to:\n{latest_file_abs}")
                self.populate_downloads()

            except Exception as e:
                messagebox.showerror("Download Error", str(e))

        threading.Thread(target=download_thread, daemon=True).start()


    # ------------------ Downloaded songs ------------------
    def populate_downloads(self):
        self.downloads_listbox.delete(0, tk.END)
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT song_id, song_name, artist_name, file_path FROM songsDownloaded ORDER BY song_id DESC")
        rows = c.fetchall()
        conn.close()
        self.downloaded_ids = []
        if not rows:
            self.downloads_listbox.insert(tk.END, "No downloads yet")
            return
        for song_id, song_name, artist, file_path in rows:
            display = f"{song_name} - {artist if artist else 'Unknown'}"
            self.downloads_listbox.insert(tk.END, display)
            self.downloaded_ids.append((song_id, file_path))

    # ------------------ Playlist ------------------
    def populate_playlists(self):
        try:
            playlists = curr_user.viewPlaylists()
        except Exception:
            playlists = []
        labels = [f"{p[1]} (ID:{p[0]})" for p in playlists]
        self.playlist_ids = [p[0] for p in playlists]
        self.playlist_combo['values'] = labels
        if labels:
            self.playlist_combo.current(0)

    def add_selected_to_playlist(self):
        sel = self.downloads_listbox.curselection()
        if not sel:
            messagebox.showwarning("Select", "Select a downloaded song first.")
            return
        idx = sel[0]
        song_id, file_path = self.downloaded_ids[idx]
        plist_index = self.playlist_combo.current()
        if plist_index == -1:
            messagebox.showwarning("Select", "Select a playlist first.")
            return
        playlist_id = self.playlist_ids[plist_index]
        pl = Playlist(DB_FILE, playlist_id)
        success, msg = pl.addSong(song_id)
        if success:
            messagebox.showinfo("Added", "Song added to playlist.")
        else:
            messagebox.showerror("Error", msg)


# -------------------------------
# 👤 ACCOUNT PAGE (LOGIN / PROFILE) simple placeholder
# -------------------------------
class AccountPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#121212")
        self.controller = controller

        top_bar = tk.Frame(self, bg="#181818", height=54)
        top_bar.pack(side="top", fill="x")
        ttk.Button(top_bar, text="Home", command=lambda: controller.show_frame(MainPage)).pack(side="left", padx=8, pady=8)
        ttk.Button(top_bar, text="Download", command=lambda: controller.show_frame(DownloadPage)).pack(side="left", padx=8, pady=8)

        body = tk.Frame(self, bg="#121212")
        body.pack(fill="both", expand=True)
        tk.Label(body, text="👤 Account / Profile (placeholder)", bg="#121212", fg="white", font=("Segoe UI", 14, "bold")).pack(pady=20)
        # small profile display (reads from DB)
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT first_name, last_name, username, profile_pic FROM users WHERE user_id = ?", (curr_user.user_id,))
        row = c.fetchone()
        conn.close()
        if row:
            first, last, username, pic = row
            tk.Label(body, text=f"{first} {last} ({username})", bg="#121212", fg="white").pack()
            if pic and os.path.exists(pic):
                img = Image.open(pic).resize((128, 128))
                tk_img = ImageTk.PhotoImage(img)
                lbl = tk.Label(body, image=tk_img)
                lbl.image = tk_img
                lbl.pack(pady=8)

# -------------------------------
# 🧭 START APPLICATION
# -------------------------------
if __name__ == "__main__":
    user_id = show_login()  # show login first
    if user_id:  # login successful
        curr_user = User(DB_FILE, user_id)
        app = MusicApp(curr_user)
        app.mainloop()
    else:
        print("Login failed or cancelled. Exiting.")
