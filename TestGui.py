import tkinter as tk
from tkinter import ttk
import subprocess
import sys
import os
from user_profile import UserProfileGUI, get_current_user
from LoginApp import show_login 

# -------------------------------
# 🏠 MAIN APPLICATION CONTROLLER
# -------------------------------
class MusicApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Offline Music Player")
        self.attributes('-fullscreen', True)
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
        ttk.Button(top_bar, text="Account", command=self.open_profile).pack(side="left", padx=10, pady=5)
        ttk.Button(top_bar, text="Add Song", command=self.add_song).pack(side="left", padx=10, pady=5)




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
    
    def add_song(self):
        from add_song import MusicDownloaderGUI  # import the class directly

        add_song_window = tk.Toplevel(self)
        add_song_window.title("Download & Add Song")
        add_song_window.geometry("550x400")
        current_user = get_current_user() 
        app = MusicDownloaderGUI(add_song_window, current_user)
    def open_profile(self):
        profile_window = tk.Toplevel(self)
        profile_window.title("User Profile")
        profile_window.geometry("600x500")
        current_user = get_current_user()
        UserProfileGUI(profile_window, current_user)  # pass the Toplevel




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
    user_id = show_login()  # open login window first
    if user_id:  # login successful
        app = MusicApp()
        app.mainloop()
    else:
        print("Login cancelled or failed. Exiting...")

