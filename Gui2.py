import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import os
from Classes import User, Playlist
from musicPlayer import MusicPlayer, choose_folder

DB_FILE = "musicApp.db"
curr_user = User(DB_FILE, 1)  # testing: assume user 1 is logged in

class MusicApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Offline Music Player")
        self.root.geometry("900x600")
        self.root.configure(bg="#121212")

        # --- Elijah's Testing ---
        #self.playlist = choose_folder()  # opens file dialog and gets all songs in a folder
        #self.player = MusicPlayer(self.playlist)

        # We are gonna need to create a local folder, (so a folder on your computer) that stores all downloaded songs
        # and then we can set that as the default music folder for the player (we can either make a thing to create it)
        # or just tell the user to create a folder and select it the first time they run the app
        # We also need to change our database to store a local download folder
        # Ill probably keep the choose_folder function and use it to select the download folder
        # and then we can store that in the database for the user

        # currently selected playlist id
        self.current_playlist_id = None
        self.playlist_ids = []

        # --- Responsive grid setup ---
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)

        # --- Styles ---
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background="#181818", foreground="white", font=("Segoe UI", 10))
        style.configure("TButton", background="#1DB954", foreground="white", font=("Segoe UI", 10, "bold"))
        style.map("TButton", background=[("active", "#1ED760")])

        # --- Top Bar ---
        self.top_bar = tk.Frame(self.root, bg="#181818", height=100)
        self.top_bar.grid(row=0, column=0, sticky="nsew")
        self.top_bar.grid_propagate(False)
        tk.Label(self.top_bar, text="🎵 Offline Music Player", fg="white", bg="#181818",
                 font=("Segoe UI", 12, "bold")).pack(side="left", padx=15, pady=10)
        ttk.Button(self.top_bar, text="Account").pack(fill="x", side=tk.LEFT, padx=10, pady=4)
        ttk.Button(self.top_bar, text="Download").pack(fill="x", side=tk.LEFT,padx=10, pady=4)

        # --- Main Content ---
        self.main_frame = tk.Frame(self.root, bg="#121212")
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=2)
        self.main_frame.columnconfigure(2, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

        # --- Left: Playlists ---
        self.playlist_frame = tk.Frame(self.main_frame, bg="#181818")
        self.playlist_frame.grid(row=0, column=0, sticky="nsew", padx=5)
        tk.Label(self.playlist_frame, text="Playlists", fg="white", bg="#181818",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=10, pady=5)
        self.playlist_box = tk.Listbox(self.playlist_frame, bg="#202020", fg="white",
                                       selectbackground="#404040", highlightthickness=0, relief="flat")
        self.playlist_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.playlist_box.bind("<<ListboxSelect>>", self.show_playlist_songs)

        # --- Middle: Songs ---
        self.songs_frame = tk.Frame(self.main_frame, bg="#181818")
        self.songs_frame.grid(row=0, column=1, sticky="nsew", padx=5)
        tk.Label(self.songs_frame, text="Songs", fg="white", bg="#181818",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=10, pady=5)
        self.songs_box = tk.Listbox(self.songs_frame, bg="#202020", fg="white",
                                    selectbackground="#404040", highlightthickness=0, relief="flat")
        self.songs_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # --- Right: Playlist Controls ---
        self.controls_frame = tk.Frame(self.main_frame, bg="#181818")
        self.controls_frame.grid(row=0, column=2, sticky="nsew", padx=5)
        tk.Label(self.controls_frame, text="Playlist Controls", fg="white", bg="#181818",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=10, pady=5)

        ttk.Button(self.controls_frame, text="+ Create Playlist", command=self.create_playlist).pack(fill="x", padx=10, pady=4)
        ttk.Button(self.controls_frame, text="✏ Rename Playlist", command=self.rename_playlist_popup).pack(fill="x", padx=10, pady=4)
        ttk.Button(self.controls_frame, text="🗑 Delete Playlist", command=self.delete_playlist).pack(fill="x", padx=10, pady=4)
        ttk.Button(self.controls_frame, text="▶ Play Playlist", command=self.play_playlist).pack(fill="x", padx=10, pady=8)
        ttk.Separator(self.controls_frame, orient="horizontal").pack(fill="x", padx=10, pady=8)
        ttk.Button(self.controls_frame, text="+ Add Song", command=self.add_song_placeholder).pack(fill="x", padx=10, pady=4)
        ttk.Button(self.controls_frame, text="❌ Remove Song", command=self.remove_song).pack(fill="x", padx=10, pady=4)
        ttk.Button(self.controls_frame, text="📷 Add Cover", command=self.add_playlist_cover).pack(fill="x", padx=10, pady=4)
        ttk.Button(self.controls_frame, text="🖼 Remove Cover", command=self.delete_playlist_cover).pack(fill="x", padx=10, pady=4)

        # --- Bottom Bar ---
        self.bottom_bar = tk.Frame(self.root, bg="#181818", height=80)
        self.bottom_bar.grid(row=2, column=0, sticky="nsew")
        self.bottom_bar.grid_propagate(False)
        self.bottom_bar.columnconfigure(0, weight=1)
        self.bottom_bar.columnconfigure(1, weight=1)
        self.bottom_bar.columnconfigure(2, weight=1)

        # Song Info
        song_info = tk.Frame(self.bottom_bar, bg="#181818")
        song_info.grid(row=0, column=0, sticky="w", padx=20)
        self.song_title_label = tk.Label(song_info, text="Song Title", fg="white", bg="#181818",
                                        font=("Segoe UI", 10, "bold"))
        self.song_title_label.pack(anchor="w")
        self.song_artist_label = tk.Label(song_info, text="Artist Name", fg="#b3b3b3", bg="#181818",
                                         font=("Segoe UI", 9))
        self.song_artist_label.pack(anchor="w")

        # Player buttons
        player_controls = tk.Frame(self.bottom_bar, bg="#181818")
        player_controls.grid(row=0, column=1)
        ttk.Button(player_controls, text="⏮", command=self.player.previous_song).grid(row=0, column=0, padx=5)
        ttk.Button(player_controls, text="▶", command=self.player.toggle_play).grid(row=0, column=1, padx=5)
        ttk.Button(player_controls, text="⏭", command=self.player.next_song).grid(row=0, column=2, padx=5)

        # Volume
        volume_frame = tk.Frame(self.bottom_bar, bg="#181818")
        volume_frame.grid(row=0, column=2, sticky="e", padx=20)
        tk.Label(volume_frame, text="🔊", fg="white", bg="#181818").pack(side="left")
        ttk.Scale(volume_frame, from_=0, to=100, orient="horizontal", length=100).pack(side="left", padx=5)

        # --- Cover Image ---
        self.cover_label = tk.Label(self.controls_frame, text="No cover", bg="#181818", fg="white")
        self.cover_label.pack(pady=10)

        # Populate playlists
        self.disp_playlists()

    # -------------------- Playlist Functions -------------------- #
    def disp_playlists(self):
        self.playlist_box.delete(0, tk.END)
        self.playlist_ids = []
        playlists = curr_user.viewPlaylists()
        for pid, name in playlists:
            self.playlist_box.insert(tk.END, name)
            self.playlist_ids.append(pid)

    def create_playlist(self):
        new_id = curr_user.createNew(firstSong=1)  # dummy song
        messagebox.showinfo("Success", f"Created playlist #{new_id}")
        self.disp_playlists()

    def rename_playlist_popup(self):
        selection = self.playlist_box.curselection()
        if not selection:
            messagebox.showwarning("Oops", "Select a playlist first")
            return
        idx = selection[0]
        self.current_playlist_id = self.playlist_ids[idx]

        popup = tk.Toplevel(self.root)
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
        ttk.Button(popup, text="Rename", command=rename_action).pack(pady=5)

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
        songs = pl.viewSongs()

        self.songs_box.delete(0, tk.END)
        if songs:
            for song_id, song_name, artist, album, length in songs:
                self.songs_box.insert(tk.END, f"{song_name} - {artist}")
        else:
            self.songs_box.insert(tk.END, "No songs in this playlist")

        # Display cover
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT cover_photo FROM playlist WHERE playlist_id = ?", (self.current_playlist_id,))
        cover_path = cursor.fetchone()[0]
        conn.close()

        if cover_path and os.path.exists(cover_path):
            img = Image.open(cover_path).resize((150,150))
            tk_img = ImageTk.PhotoImage(img)
            self.cover_label.config(image=tk_img, text="")
            self.cover_label.image = tk_img
        else:
            self.cover_label.config(image="", text="No cover")

    def play_playlist(self):
        messagebox.showinfo("Play", "Playlist is now playing!")

    def remove_song(self):
        selection = self.songs_box.curselection()
        if not selection:
            messagebox.showwarning("Oops", "Select a song first")
            return
        idx = selection[0]
        song_text = self.songs_box.get(idx)
        song_name = song_text.split(" - ")[0]
        pl = Playlist(DB_FILE, self.current_playlist_id)
        # find song_id by name (simplified)
        songs = pl.viewSongs()
        target_id = None
        for s in songs:
            if s[1] == song_name:
                target_id = s[0]
                break
        if target_id:
            pl.removeSong(target_id)
            self.show_playlist_songs()
            messagebox.showinfo("Removed", f"Removed {song_name} from playlist")

    def add_song_placeholder(self):
        messagebox.showinfo("Info", "Add song functionality not implemented yet")

    def add_playlist_cover(self):
        file_path = filedialog.askopenfilename(title="Select Cover Image",
                                               filetypes=[("PNG images", "*.png"),("All files","*.*")])
        if not file_path:
            return
        pl = Playlist(DB_FILE, self.current_playlist_id)
        pl.uploadCover(file_path)
        self.show_playlist_songs()
        messagebox.showinfo("Success", "Cover image added!")

    def delete_playlist_cover(self):
        pl = Playlist(DB_FILE, self.current_playlist_id)
        pl.removeCover()
        self.show_playlist_songs()
        messagebox.showinfo("Success", "Cover image removed!")

if __name__ == "__main__":
    root = tk.Tk()
    app = MusicApp(root)
    root.mainloop()
