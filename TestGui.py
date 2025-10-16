import tkinter as tk
from tkinter import ttk
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter import PhotoImage
from tkinter import Image
import os
from tkinter import filedialog
from PIL import Image, ImageTk

from Classes import Account, User, Playlist
#from music_player import MusicPlayer
import sqlite3

DB_FILE = "musicApp.db"

# -------------------------------
# 🏠 MAIN APPLICATION CONTROLLER
# -------------------------------
class MusicApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Offline Music Player")
        self.geometry("900x600")
        self.configure(bg="#121212")

        # Container that holds all pages
        container = tk.Frame(self, bg="#121212")
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Store all pages here
        self.frames = {}
        for F in (MainPage, DownloadPage, AccountPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Show the main page on startup
        self.show_frame(MainPage)

    def show_frame(self, page_class):
        """Brings a given page to the front"""
        frame = self.frames[page_class]
        frame.tkraise()


# -------------------------------
# 🎵 MAIN PAGE (PLAYER / PLAYLIST)
# -------------------------------
class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#121212")
        self.controller = controller

        # --- Top Bar ---
        top_bar = tk.Frame(self, bg="#181818", height=50)
        top_bar.pack(side="top", fill="x")

        ttk.Button(top_bar, text="Home",
                   command=lambda: controller.show_frame(MainPage)).pack(side="left", padx=10, pady=5)
        ttk.Button(top_bar, text="Download",
                   command=lambda: controller.show_frame(DownloadPage)).pack(side="left", padx=10, pady=5)
        ttk.Button(top_bar, text="Account",
                   command=lambda: controller.show_frame(AccountPage)).pack(side="left", padx=10, pady=5)

        # --- Main Area ---
        main_content = tk.Frame(self, bg="#202020")
        main_content.pack(fill="both", expand=True)
        tk.Label(main_content, text="🎧 Main Player Page (Coming Soon)",
                 bg="#202020", fg="white", font=("Segoe UI", 14, "bold")).pack(expand=True)

        # --- Bottom Bar ---
        bottom_bar = tk.Frame(self, bg="#181818", height=60)
        bottom_bar.pack(side="bottom", fill="x")
        tk.Label(bottom_bar, text="Playback controls will go here",
                 bg="#181818", fg="#B3B3B3", font=("Segoe UI", 10)).pack(pady=10)


# -------------------------------
# ⬇️ DOWNLOAD PAGE
# -------------------------------
class DownloadPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#121212")
        self.controller = controller

        top_bar = tk.Frame(self, bg="#181818", height=50)
        top_bar.pack(side="top", fill="x")
        ttk.Button(top_bar, text="Home",
                   command=lambda: controller.show_frame(MainPage)).pack(side="left", padx=10, pady=5)
        ttk.Button(top_bar, text="Account",
                   command=lambda: controller.show_frame(AccountPage)).pack(side="left", padx=10, pady=5)

        tk.Label(self, text="⬇️ Download Page (YouTube Downloader Coming Soon)",
                 bg="#121212", fg="white", font=("Segoe UI", 14, "bold")).pack(expand=True)



____________________________________________
#I don't know how this fits into the class with the tkinter stuff but here's what was in my file for the downloads page - A :)
#like the functions and then the window details

    downloaded_ids = []

    def disp_downloaded():
        DownloadsListbox.delete(0, tk.END)
    
    
        conn = sqlite3.connect(curr_user.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT song_id, song_name FROM songsDownloaded")
        result = cursor.fetchall()
        conn.close()
    
        if not result:
            song_name = "No songs"
            song_id = None
        else:
            song_id, song_name = result
    
        if result:
            for song_id, song_name in result:
                DownloadsListbox.insert(tk.END, f"{song_name}")
                downloaded_ids.append(song_id)
        else:
            DownloadsListbox.insert(tk.END, "No songs downloaded yet")
    
    
    
    def chooseAPlaylist(event):
        selection = DownloadsListbox.curselection()
        if not selection:
            return
        index = selection[0]
        selectedSong = downloaded_ids[index]
        # selectedSong = the songid of selection
    
        playlist_ids = []
        #needs to show another playlistListbox here that have list of current user's playlists
        playlistListbox.delete(0, tk.END)
        playlists = curr_user.viewPlaylists()
        for playlistID, name in playlists:
            playlistListbox.insert(tk.END, f"{name}")
            playlist_ids.append(playlistID)
    
        #playlist_id = playlist id of playlistChosen
    
        #then show playlists
        playlistListbox.pack()
    
        #add song function
        playlistChosen = playlistListbox.curselection()
        if not playlistChosen:
            return
        index1 = playlistChosen[0]
        playlist_id = playlist_ids[index1]
    
        pl = Playlist(DB_FILE, playlist_id)
        pl.addSong(selectedSong)
    
    def search(event = None):
        #this needs to get the input from the enter box, and find the songs with the same name (start with exact same)
        conn = sqlite3.connect(curr_user.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT song_id, song_name FROM songsDownloaded")
        data_items = cursor.fetchall()
        conn.close()
    
        if not data_items:
            song_name = "No songs"
            song_id = None
        else:
            song_id, song_name = data_items
    
        if data_items:
            query = search_var.get().lower()
            DownloadsListbox.delete(0, tk.END)  # Clear previous results
    
            if not query:
                # If search box is empty, display all items (or nothing)
                for song_name in data_items:
                    DownloadsListbox.insert(tk.END, song_name)
                return
    
            found_results = [song_name for song_name in data_items if query in song_name.lower()]
    
            if found_results:
                for song_name in found_results:
                    DownloadsListbox.insert(tk.END, song_name)
                    downloaded_ids.append(song_id)
            else:
                DownloadsListbox.insert(tk.END, "No results found.")
    
        
    
    # Tkinter setup 
    root = tk.Tk()
    root.title("Downloaded Songs")
    
    downloadsTitle = tk.Label(root, text= "Downloaded Songs", font=("Arial", 25, "bold"))
    downloadsTitle.pack()
    
    #have a search bar for songs
    searchLabel = tk.Label(root, text='Search')
    searchLabel.pack()
    e1 = Entry(root)
    e1.bind("<KeyRelease>", search)
    e1.pack()
    search_var = tk.StringVar()
    tk.Button(root, text="Search", command=search).pack()
    
    
    #display the songs in the playlist in a list
    DownloadsListbox = tk.Listbox(root, width=50, height=25)
    DownloadsListbox.bind("<<ListboxSelect>>", chooseAPlaylist)
    DownloadsListbox.pack()
    
    
    
    #this needs to appear when a song is selected in downloads listbox, and is given that song's id
    # Playlist list
    playlistListbox = tk.Listbox(root, width=20, height=25)
    #playlistListbox.bind("<<ListboxSelect>>")
    playlistListbox.pack_forget()
    
    disp_downloaded()
    
    
    root.mainloop()
# Here is the end of my part -A :)
_________________________________________





# -------------------------------
# 👤 ACCOUNT PAGE (LOGIN / PROFILE)
# -------------------------------
class AccountPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#121212")
        self.controller = controller

        top_bar = tk.Frame(self, bg="#181818", height=50)
        top_bar.pack(side="top", fill="x")
        ttk.Button(top_bar, text="Home",
                   command=lambda: controller.show_frame(MainPage)).pack(side="left", padx=10, pady=5)
        ttk.Button(top_bar, text="Download",
                   command=lambda: controller.show_frame(DownloadPage)).pack(side="left", padx=10, pady=5)

        tk.Label(self, text="👤 Account / Login Page (Coming Soon)",
                 bg="#121212", fg="white", font=("Segoe UI", 14, "bold")).pack(expand=True)


# -------------------------------
# 🧭 START APPLICATION
# -------------------------------
if __name__ == "__main__":
    app = MusicApp()
    app.mainloop()
