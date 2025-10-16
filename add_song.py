import os
import sqlite3
import yt_dlp
import tkinter as tk
from tkinter import ttk, messagebox

DB_FILE = "musicApp.db"
DOWNLOAD_DIR = "downloads"
MAX_RESULTS = 5

# Database function
def get_current_user():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT u.user_id, u.username FROM current_user cu JOIN users u ON cu.user_id = u.user_id")
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {"id": user[0], "username": user[1]}
    else:
        return None

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

# Youtube function
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

# GUI
class MusicDownloaderGUI:
    def __init__(self, root, current_user):
        self.root = root
        root.title("YouTube Music Downloader & Playlist")
        root.geometry("550x400")
        root.config(bg="white")  # all white background

        self.user_id = current_user["id"]
        self.username = current_user["username"]

        self.font_label = ("Arial", 12)
        self.font_button = ("Arial", 11, "bold")
        
        top_bar = tk.Frame(root, bg="#f0f0f0", height=40)
        top_bar.pack(side="top", fill="x")
        exit_button = tk.Button(top_bar, text="✖", font=("Arial", 12, "bold"), fg="red",
                        bg="#f0f0f0", bd=0, command=root.destroy)
        exit_button.pack(side="right", padx=10, pady=5)
    
        main_frame = tk.Frame(root, bg="white")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        user_label = tk.Label(main_frame, text=f"Logged in as: {self.username}", font=("Arial", 13, "bold"), bg="white", fg="black")
        user_label.pack(pady=10)

        playlist_frame = tk.LabelFrame(main_frame, text="Select Playlist", bg="white", fg="black", font=self.font_label, bd=1, relief="solid")
        playlist_frame.pack(fill="x", pady=10, padx=10)

        self.playlist_var = tk.StringVar()
        self.playlist_dropdown = ttk.Combobox(playlist_frame, textvariable=self.playlist_var, state="readonly", width=40, font=self.font_label)
        self.playlist_dropdown.pack(pady=10, padx=10)
        self.load_playlists()

        song_frame = tk.LabelFrame(main_frame, text="Download Song", bg="white", fg="black", font=self.font_label, bd=1, relief="solid")
        song_frame.pack(fill="x", pady=10, padx=10)

        tk.Label(song_frame, text="Song Name:", bg="white", fg="black", font=self.font_label).pack(anchor="w", padx=10, pady=(10, 0))
        self.song_entry = tk.Entry(song_frame, width=40, font=self.font_label, fg="black", bg="white", bd=1, relief="solid", insertbackground="black")
        self.song_entry.pack(pady=5, padx=10)

        download_btn = tk.Button(song_frame, text="Download & Add to Playlist", bg="white", fg="black",
                                 font=self.font_button, width=30, height=2, bd=1, relief="solid", command=self.download_and_add)
        download_btn.pack(pady=15)

    def load_playlists(self):
        playlists = get_user_playlists(self.user_id)
        self.playlists = playlists
        self.playlist_dropdown['values'] = [f"{p[1]} (ID:{p[0]})" for p in playlists]
        if playlists:
            self.playlist_dropdown.current(0)

    def download_and_add(self):
        playlist_index = self.playlist_dropdown.current()
        song_query = self.song_entry.get().strip()

        if playlist_index == -1 or not song_query:
            messagebox.showerror("Error", "Select a playlist and enter song name.")
            return

        playlist_id = self.playlists[playlist_index][0]
        user_folder = os.path.join(DOWNLOAD_DIR, self.username)

        results = search_youtube(song_query)
        if not results:
            messagebox.showinfo("No Results", "No YouTube videos found.")
            return
        video_url = results[0]['webpage_url']

        metadata = download_youtube_audio(video_url, user_folder)
        song_id = add_song_to_db(
            DB_FILE,
            song_name=metadata['song_name'],
            artist_name=metadata['artist_name'],
            length=metadata['length'],
            file_path=metadata['file_path'],
            cover_art=metadata['cover_art']
        )

        success, msg = add_song_to_playlist(playlist_id, song_id)
        if success:
            messagebox.showinfo("Success", f"Downloaded '{metadata['song_name']}' and added to playlist!")
        else:
            messagebox.showerror("Error", msg)


if __name__ == "__main__":
    current_user = get_current_user()
    if not current_user:
        tk.messagebox.showerror("Error", "No user logged in!")
        exit()

    root = tk.Tk()
    root.title("YouTube Music Downloader & Playlist")
    
    # Make fullscreen
    root.attributes('-fullscreen', True)

    app = MusicDownloaderGUI(root, current_user)
    root.mainloop()
