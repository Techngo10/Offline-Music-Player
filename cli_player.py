# cli_player.py
from music_player import MusicPlayer

playlist = [
    "songs/Billie Jean - Michael Jackson.mp3",
    "songs/Fallen Kingdom - A Minecraft Parody of Coldplay's Viva la Vida (Music Video) - CaptainSparklez.mp3",
    "songs/War - Why Can't We Be Friends - Rodrigo Lima.mp3"
]

player = MusicPlayer(playlist)

while True:
    cmd = input("Enter command (play/pause/next/prev/shuffle/loop/quit): ").strip().lower()
    
    if cmd == "play": player.play()
    elif cmd == "pause": player.pause()
    elif cmd == "resume": player.resume()
    elif cmd == "stop": player.stop()
    elif cmd == "next": player.next_song()
    elif cmd == "prev": player.previous_song()
    elif cmd == "shuffle": player.toggle_shuffle()
    elif cmd == "loop": player.toggle_loop()
    elif cmd == "quit": break
    else: print("Unknown command.")
