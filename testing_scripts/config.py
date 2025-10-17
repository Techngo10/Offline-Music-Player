# populate_db.py
import sqlite3
from configurations import DB_FILE, initialize_database

initialize_database()

def populate_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    users = [
        ("Alice", "Smith", "alice@example.com", "alice123", "password1", "1234567890", ""),
        ("Bob", "Johnson", "bob@example.com", "bobj", "password2", "0987654321", ""),
        ("Charlie", "Lee", "charlie@example.com", "charlie_l", "password3", "1112223333", "")
    ]
    for first, last, email, username, password, phone, pic in users:
        try:
            cursor.execute("""
                INSERT INTO users (first_name, last_name, email, username, password, phone_no, profile_pic)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (first, last, email, username, password, phone, pic))
        except sqlite3.IntegrityError:
            pass  # skip if username already exists

    # Get user IDs for reference
    cursor.execute("SELECT user_id, username FROM users")
    user_ids = {username: uid for uid, username in cursor.fetchall()}

    songs = [
        ("Artist A", "Song One", "Album Alpha", "Lyrics 1", 3.5, "/path/song1.mp3", "/path/cover1.jpg"),
        ("Artist B", "Song Two", "Album Beta", "Lyrics 2", 4.0, "/path/song2.mp3", "/path/cover2.jpg"),
        ("Artist C", "Song Three", "Album Gamma", "Lyrics 3", 2.8, "/path/song3.mp3", "/path/cover3.jpg"),
    ]
    for artist, name, album, lyrics, length, path, cover in songs:
        try:
            cursor.execute("""
                INSERT INTO songsDownloaded (artist_name, song_name, album_name, lyrics, length, file_path, cover_art)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (artist, name, album, lyrics, length, path, cover))
        except sqlite3.IntegrityError:
            pass

    # Get song IDs for reference
    cursor.execute("SELECT song_id, song_name FROM songsDownloaded")
    song_ids = {name: sid for sid, name in cursor.fetchall()}

    playlists = [
        ("Alice's Favorites", "", user_ids.get("alice123"), ["Song One", "Song Two"]),
        ("Bob's Mix", "", user_ids.get("bobj"), ["Song Two", "Song Three"]),
    ]
    for playlist_name, cover, user_id, song_list in playlists:
        cursor.execute("""
            INSERT INTO playlist (playlist_name, cover_photo, user_id)
            VALUES (?, ?, ?)
        """, (playlist_name, cover, user_id))
        playlist_id = cursor.lastrowid

        for song_name in song_list:
            song_id = song_ids.get(song_name)
            if song_id:
                cursor.execute("""
                    INSERT INTO playlist_songs (playlist_id, song_id)
                    VALUES (?, ?)
                """, (playlist_id, song_id))

    cursor.execute("DELETE FROM current_user")
    cursor.execute("INSERT INTO current_user (user_id) VALUES (?)", (user_ids.get("alice123"),))

    conn.commit()
    conn.close()
    print("Database populated with sample data!")

if __name__ == "__main__":
    populate_db()
