# Offline-Music-Player

A simple offline music player built in Python using `pygame`.  
Utilizes yt-dlp libary to download mp3 files from youtube, aimed at people who like songs exclusive to youtube and want to save them
Supports play, pause, next/previous track, cover art, and user accounts.

---

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

6. Run the CLI player
```
python cli_player.py
```

| Command | Description                           |
| ------- | ------------------------------------- |
| play    | Play current song (resumes if paused) |
| pause   | Pause current song                    |                  |
| next    | Play next song                        |
| prev    | Play previous song                    |
| shuffle | Toggle shuffle mode                   |
| loop    | Toggle loop mode                      |
| quit    | Exit the program                      |

