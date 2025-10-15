import sqlite3

# Create User table
conn = sqlite3.connect("musicApp.db")
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS current_user (
        user_id INTEGER UNIQUE,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    username TEXT UNIQUE,
    password TEXT,
    phone_no INTEGER,
    profile_pic TEXT
    )
    """)

# Create songs downloaded table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS songsDownloaded (
    song_id INTEGER PRIMARY KEY AUTOINCREMENT,
    artist_name TEXT,
    song_name TEXT,
    album_name TEXT,
    lyrics TEXT,
    length REAL
    file_path TEXT,
    cover_art TEXT
    )
    """)

# Create playlist table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS playlist (
    playlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
    playlist_name TEXT,
    cover_photo TEXT,
    user_id INTEGER,
    FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
    """)


# create playlist songs table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS playlist_songs (
    playlist_id INTEGER,
    song_id INTEGER,
    PRIMARY KEY (playlist_id, song_id),
    FOREIGN KEY(playlist_id) REFERENCES playlist(playlist_id),
    FOREIGN KEY(song_id) REFERENCES songsDownloaded(song_id)
    )
    """)


conn.commit()
conn.close()