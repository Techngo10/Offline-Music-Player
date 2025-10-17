# Offline-Music-Player

A simple offline music player built in Python using `pygame`.  
Utilizes yt-dlp libary to download mp3 files from youtube, aimed at people who like songs exclusive to youtube and want to save them
Supports play, pause, next/previous track, cover art, and user accounts.

About Repository structure: 
Offline-Music-Player/
├── Classes.py                 # Defines the core classes: User and Playlist. Handles all DB operations for users, playlists, and songs.
├── Databases.py               # Initializes the SQLite database and creates all required tables.
├── LoginApp.py                # Manages user login functionality. Returns user ID after successful login.
├── add_song.py                # Handles downloading songs from YouTube using yt-dlp and adding them to the database.
├── musicPlayer.py             # Implements the low-level music player functionality (play, pause, next, previous, volume).
├── DownloadsPageGUI.py        # GUI logic for the download page, including adding songs to playlists.
├── user_profile.py            # GUI for displaying and managing the current user’s profile.
├── mainFinal.py / gui_combined.py  # Optional/main testing scripts combining different GUI components.
├── requirements.txt           # Lists all Python dependencies needed to run the project.
├── downloads/                 # Folder where downloaded audio files are stored.
├── musicApp.db                # SQLite database file (created after running Databases.py).
├── README.md                  # This file.

------------------------------------------------------------------------------------------------------------------------------------------------------------------

## Setup Instructions

1. **Clone the repository**
```bash
git clone https://github.com/Techngo10/Offline-Music-Player
cd Offline-Music-Player
```

2. Set up the virtual environment
```
python -m venv .venv
```

3. Activate your virtual enviourment
```
Windows (PowerShell / CMD):
.venv\Scripts\activate

Mac/Linux:
source .venv/bin/activate
```

4. Install all dependencies from requirements.txt
```
pip install -r requirements.txt
```

5. Verify installation
```
pip list
```

6. Delete the existing Database to start fresh
```
rm musicApp.db
```

7. Initialize your database
```
python Databases.py 
```

8. Go ahead and run the music player, UI should be quite intuitive
```
python mainFinal.py
```



