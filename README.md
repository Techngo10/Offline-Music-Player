# Offline-Music-Player

A simple offline music player built in Python using `pygame`.  
Supports play, pause, resume, stop, next/previous track, shuffle, and loop.

---

## Setup Instructions

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd Offline-Music-Player
```

2. Set up the virtual environment
```
python -m venv .venv
```

4. Activate it in powershell terminal and run
```
.venv\Scripts\activate
.venv\Scripts\activate.bat
```

5. Run the needed python dependencies
```
pip install pygame
```

7. Add music files
```
 └── songs/
     ├── songname.mp3
     ├── songname.mp3
     └── songname.mp3
```

9. Run the CLI player
```
python cli_player.py
```

| Command | Description                           |
| ------- | ------------------------------------- |
| play    | Play current song (resumes if paused) |
| pause   | Pause current song                    |
| resume  | Resume paused song                    |
| stop    | Stop playback                         |
| next    | Play next song                        |
| prev    | Play previous song                    |
| shuffle | Toggle shuffle mode                   |
| loop    | Toggle loop mode                      |
| quit    | Exit the program                      |

