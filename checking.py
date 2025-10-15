import sqlite3

DB_FILE = "musicApp.db"

def show_downloaded_songs():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT song_id, song_name, artist_name, album_name, length 
        FROM songsDownloaded
    """)
    
    songs = cursor.fetchall()
    conn.close()
    
    if not songs:
        print("No songs found in the database.")
        return

    print(f"{'ID':<5} {'Song Name':<30} {'Artist':<25} {'Album':<25} {'Length(s)':<10}")
    print("-" * 100)
    for song in songs:
        song_id, name, artist, album, length = song
        print(f"{song_id:<5} {name:<30} {artist or 'N/A':<25} {album or 'N/A':<25} {length or 'N/A':<10}")

if __name__ == "__main__":
    show_downloaded_songs()
