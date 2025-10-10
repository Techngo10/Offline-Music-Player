import os
import sqlite3
import yt_dlp
import tkinter as tk
from tkinter import ttk, messagebox

DB_FILE = "musicApp.db"
DOWNLOAD_DIR = "downloads"
MAX_RESULTS = 5

# ----------------- Database functions -----------------
def get_all_users():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def get_user_playlists(user_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT playlist_id, playlist_name FROM playlist WHERE user_id = ?", (user_id,))
    playlists = cursor.fetchall()
    conn.close()
    return playlists

def add_song_to_db(db_file, song_name, artist_name=None, album_name=None, lyrics=None, length=None, file_path=None, cover_art=None):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO songsDownloaded (song_name, artist_name, album_name, lyrics, length, file_path, cover_art)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (song_name, artist_name, album_name, lyrics, length, file_path, cover_art))
    song_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return song_id

def add_song_to_playlist(playlist_id, song_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO playlist_songs (playlist_id, song_id) VALUES (?, ?)", (playlist_id, song_id))
        conn.commit()
        return True, "Song added successfully to playlist!"
    except sqlite3.IntegrityError:
        return False, "Song is already in the playlist."
    finally:
        conn.close()

# ----------------- YouTube download -----------------
def search_youtube(query, max_results=MAX_RESULTS):
    ydl_opts = {'quiet': True, 'skip_download': True, 'default_search': f'ytsearch{max_results}'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        search_results = ydl.extract_info(query, download=False)
        return search_results['entries']

def download_youtube_audio(video_url, user_folder):
    os.makedirs(user_folder, exist_ok=True)
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(user_folder, '%(title)s [%(id)s].%(ext)s'),
        'postprocessors': [
            {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'},
            {'key': 'EmbedThumbnail'},
            {'key': 'FFmpegMetadata'}
        ],
        'writethumbnail': True,
        'quiet': False,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=True)
        filename = ydl.prepare_filename(info_dict)
        mp3_file = os.path.splitext(filename)[0] + ".mp3"

    metadata = {
        'song_name': info_dict.get('title'),
        'artist_name': info_dict.get('uploader'),
        'length': info_dict.get('duration'),
        'cover_art': info_dict.get('thumbnail'),
        'file_path': mp3_file
    }
    return metadata

# ----------------- GUI -----------------
class MusicDownloaderGUI:
    def __init__(self, root):
        self.root = root
        root.title("YouTube Music Downloader & Playlist")
        root.geometry("550x400")

        # --- Select User ---
        tk.Label(root, text="Select User:", font=("Arial", 12)).pack(pady=5)
        self.user_var = tk.StringVar()
        self.users = get_all_users()
        self.user_dropdown = ttk.Combobox(root, textvariable=self.user_var, state="readonly")
        self.user_dropdown['values'] = [f"{u[1]} (ID:{u[0]})" for u in self.users]
        self.user_dropdown.pack(pady=5)
        self.user_dropdown.bind("<<ComboboxSelected>>", self.load_playlists)

        # --- Select Playlist ---
        tk.Label(root, text="Select Playlist:", font=("Arial", 12)).pack(pady=5)
        self.playlist_var = tk.StringVar()
        self.playlist_dropdown = ttk.Combobox(root, textvariable=self.playlist_var, state="readonly")
        self.playlist_dropdown.pack(pady=5)

        # --- Song Search ---
        tk.Label(root, text="Song Name to Download:", font=("Arial", 12)).pack(pady=5)
        self.song_entry = tk.Entry(root, width=40, font=("Arial", 12))
        self.song_entry.pack(pady=5)

        # --- Download Button ---
        tk.Button(root, text="Download & Add to Playlist", command=self.download_and_add, bg="#4A90E2", fg="white").pack(pady=15)

    def load_playlists(self, event=None):
        user_index = self.user_dropdown.current()
        if user_index == -1:
            return
        self.user_id = self.users[user_index][0]
        playlists = get_user_playlists(self.user_id)
        self.playlists = playlists
        self.playlist_dropdown['values'] = [f"{p[1]} (ID:{p[0]})" for p in playlists]
        if playlists:
            self.playlist_dropdown.current(0)

    def download_and_add(self):
        user_index = self.user_dropdown.current()
        playlist_index = self.playlist_dropdown.current()
        song_query = self.song_entry.get().strip()

        if user_index == -1 or playlist_index == -1 or not song_query:
            messagebox.showerror("Error", "Select user, playlist, and enter song name.")
            return

        playlist_id = self.playlists[playlist_index][0]
        user_folder = os.path.join(DOWNLOAD_DIR, self.users[user_index][1])

        # Search YouTube
        results = search_youtube(song_query)
        if not results:
            messagebox.showinfo("No Results", "No YouTube videos found.")
            return
        video_url = results[0]['webpage_url']

        # Download song
        metadata = download_youtube_audio(video_url, user_folder)
        song_id = add_song_to_db(
            DB_FILE,
            song_name=metadata['song_name'],
            artist_name=metadata['artist_name'],
            length=metadata['length'],
            file_path=metadata['file_path'],
            cover_art=metadata['cover_art']
        )

        # Add to playlist
        success, msg = add_song_to_playlist(playlist_id, song_id)
        if success:
            messagebox.showinfo("Success", f"Downloaded '{metadata['song_name']}' and added to playlist!")
        else:
            messagebox.showerror("Error", msg)

# ----------------- Run App -----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = MusicDownloaderGUI(root)
    root.mainloop()
