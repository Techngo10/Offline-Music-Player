import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter import PhotoImage
from tkinter import Image
import os

from Classes import Account, User, Playlist
import sqlite3

DB_FILE = "musicApp.db"

# for testing, pretend user 1 is logged in
curr_user = User(DB_FILE, 1)

# Global list to store playlist IDs parallel to the listbox items
playlist_ids = []
current_playlist_id = None #to say which playlist is currently viewed/edited



def disp_playlists():
    """Display user's playlists in the listbox."""
    listbox.delete(0, tk.END)
    playlists = curr_user.viewPlaylists()
    for playlistID, name in playlists:
        listbox.insert(tk.END, f"{name}")
        playlist_ids.append(playlistID)


def create_playlist():
    """Create a new playlist with a dummy song id."""
    try:
        new_playlist_id = curr_user.createNew(firstSong=1)  # test song id 1
        messagebox.showinfo("Success", f"Created new playlist #{new_playlist_id}")
        disp_playlists()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def rename_playlist():
    """Change selection playlist's name."""
    #get selected playlist's id and from there update name
    global current_playlist_id
    new_name = name_entry.get().strip()
    
    pl = Playlist(DB_FILE, current_playlist_id)
    pl.changePlaylistName(new_name)
    disp_playlists()
    playlist_label.config(text=new_name)


def delete_playlist():
    """Delete selection playlist."""
    global current_playlist_id
    global playlist_ids

    pl = Playlist(DB_FILE, current_playlist_id)
    pl.deletePlaylist()

    if current_playlist_id in playlist_ids:
        index_to_remove = playlist_ids.index(current_playlist_id)
        playlist_ids.pop(index_to_remove)

    current_playlist_id = 0
    messagebox.showinfo("Deleted", "Playlist deleted.")

    disp_playlists()
    songsListbox.delete(0, tk.END)

def showPlaylistSongs(event):
    #Display palylist's songs in the listbox.
    selection = listbox.curselection()
    if not selection:
        return
    
    index = selection[0]
    playlist_id = playlist_ids[index]

    global current_playlist_id
    current_playlist_id = playlist_id

    conn = sqlite3.connect(curr_user.db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT playlist_name, cover_photo FROM playlist WHERE playlist_id = ?", (playlist_id,))
    result = cursor.fetchone()
    conn.close()

    if not result:
        playlist_name = "Unknown Playlist"
        cover_path = None
    else:
        playlist_name, cover_path = result

    playlist_label.config(text=playlist_name) #change label to playlist name
    #playlistCover.config(image = coverImage)

   #display cover image
    if cover_path and os.path.exists(cover_path):
        try:
            img = Image.open(cover_path)
            img = img.resize((200, 200))
            tk_img = ImageTk.PhotoImage(img)

            playlistCover.config(image=tk_img, text="")
            playlistCover.image = tk_img  # prevent garbage collection
        except Exception as e:
            playlistCover.config(text="Error loading image", image="")
            playlistCover.image = None
    else:
        playlistCover.config(text="No cover image", image="")
        playlistCover.image = None

    # get songs
    pl = Playlist(DB_FILE, playlist_id)
    songs = pl.viewSongs()

    songsListbox.delete(0, tk.END)
    if songs:
        for song in songs:
            songsListbox.insert(tk.END, song)
    else:
        songsListbox.insert(tk.END, "No songs in this playlist yet")


#def AddSongs():
    

def RemoveSong():
    """Delete selected song"""
    selection = songsListbox.curselection()
    if not selection:
        messagebox.showwarning("Oops", "Please select a song to delete")
        return
    global current_playlist_id  

    song_info = songsListbox.get(selection[0])
    pl = Playlist(DB_FILE, current_playlist_id)
    pl.removeSong(song_info)
    disp_playlists()


def AddPlaylistCover():
     #upload new playlist cover

    global current_playlist_id  

    file_types = [("PNG images", "*.png"),("all files","*.*")]

    files = tk.Toplevel()
    files.withdraw()
    file_path = filedialog.askopenfilename(title="Select Cover Image", filetypes=file_types, parent = files)
    files.destroy()

    if not file_path:
        return  # user cancelled

    pl = Playlist(DB_FILE, current_playlist_id)
    pl.uploadCover(file_path) 
    disp_playlists()

def deletePlaylistCover():
    #delete playlist cover
    global current_playlist_id  

    pl = Playlist(DB_FILE, current_playlist_id)
    pl.removeCover()
    disp_playlists()
    


def playPlaylist():
    #i have no idea on this button's functionality I think its somewhere else
    messagebox.showinfo("yay", "Playlist is playing")



# Tkinter setup 
root = tk.Tk()
root.title("Playlist Manager")

# left frame
left_frame = tk.Frame(root)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# right frame
right_frame = tk.Frame(root)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

#playlist Title
playlistTitle = tk.Label(left_frame, text = "Playlists", font=("Arial", 25, "bold"),)
playlistTitle.pack(side=TOP, anchor=NW, padx=15)

# Playlist list
listbox = tk.Listbox(left_frame, width=20, height=25)
listbox.pack(anchor=W, padx = 15)
listbox.bind("<<ListboxSelect>>", showPlaylistSongs)

#vertical divider
separator = ttk.Separator(root, orient=tk.VERTICAL)
separator.pack(side=tk.LEFT, fill=tk.Y, padx=5)

#inside playlist

#playlist cover disp
playlistCover = tk.Label(right_frame)
playlistCover.grid(row = 0, column=0, padx=5, pady=5)

#playlist name disp
playlist_label = tk.Label(right_frame, text = "Playlist Name", font=("Arial", 25, "bold"))
playlist_label.grid(row=0, column=1, padx=5, pady=5)

# Input for renaming
name_entry = tk.Entry(right_frame, width=25)
name_entry.grid(row=1, column=0, padx=5, pady=5)
name_entry.insert(0, "Enter new playlist name here")

#edit playlist name
editPlaylistName = tk.Button(right_frame, text="Rename Playlist", command=rename_playlist)
editPlaylistName.grid(row=1, column=1, padx=5, pady=5)

#display the songs in the playlist in a list
songsListbox = tk.Listbox(right_frame, width=50, height=25)
songsListbox.grid(row=2, column=1)

# Buttons
#tk.Button(root, text="Playlists", command=disp_playlists).pack(pady=2) #should be in top menu bar
tk.Button(left_frame, text="Create Playlist", command=create_playlist).pack(anchor=W, padx = 15)
tk.Button(right_frame, text="Delete Playlist", command=delete_playlist).grid(row = 2, column= 0)
#tk.Button(right_frame, text="Add Songs", command=AddSongs).pack(anchor=W, pady=5) maybe we should put this with the songs? I don't know
tk.Button(right_frame, text="Remove Song", command=RemoveSong).grid(row = 3, column= 0)
tk.Button(right_frame, text="Add/Change Playlist Cover", command=AddPlaylistCover).grid(row = 4, column= 0)
tk.Button(right_frame, text="Delete Playlist Cover", command=deletePlaylistCover).grid(row = 5, column= 0)
tk.Button(right_frame, text="Play", command=playPlaylist).grid(row = 6, column= 0)


root.grid_rowconfigure(1, weight=1) # Row 1 expands vertically
root.grid_columnconfigure(0, weight=1) # Column 0 expands horizontally

# Start by loading the playlists
disp_playlists()

root.mainloop()