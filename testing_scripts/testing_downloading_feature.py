# test_add_song.py
import os
import sys
import shutil
import sqlite3

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from add_song import (
    DB_FILE,
    DOWNLOAD_DIR,
    get_current_user,
    add_song_to_db,
    add_song_to_playlist,
    search_youtube,
    download_youtube_audio
)

# --- Ensure database schema exists ---
def initialize_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS songsDownloaded (
        song_id INTEGER PRIMARY KEY AUTOINCREMENT,
        song_name TEXT NOT NULL,
        artist_name TEXT,
        album_name TEXT,
        lyrics TEXT,
        length INTEGER,
        file_path TEXT,
        cover_art TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS playlist_songs (
        playlist_id INTEGER,
        song_id INTEGER,
        PRIMARY KEY (playlist_id, song_id)
    )
    """)

    conn.commit()
    conn.close()

# --- Tests ---
def test_youtube_search():
    print("Testing YouTube search...")
    results = search_youtube("Rick Astley Never Gonna Give You Up", max_results=1)
    assert results, "Search returned no results!"
    print("Search test passed!")

def test_audio_download():
    print("Testing YouTube audio download...")
    test_user_folder = os.path.join(DOWNLOAD_DIR, "test_user")
    os.makedirs(test_user_folder, exist_ok=True)

    results = search_youtube("Rick Astley Never Gonna Give You Up", max_results=1)
    video_url = results[0]['webpage_url']
    metadata = download_youtube_audio(video_url, test_user_folder)

    assert os.path.exists(metadata['file_path']), "MP3 file was not downloaded!"
    assert metadata['song_name'], "Metadata missing song name!"
    assert metadata['artist_name'], "Metadata missing artist name!"
    print(f"Downloaded '{metadata['song_name']}' by {metadata['artist_name']}")
    print("Download test passed!")

    # Clean up test download
    shutil.rmtree(test_user_folder)

def test_database_functions():
    print("Testing database insert functions...")

    # Add a fake song
    song_id = add_song_to_db(
        DB_FILE,
        song_name="Test Song",
        artist_name="Test Artist",
        length=123,
        file_path="/path/to/file.mp3",
        cover_art=None
    )
    print(f"Inserted song with ID: {song_id}")

    success, msg = add_song_to_playlist(playlist_id=1, song_id=song_id)
    print(f"Add to playlist: {msg}")
    
def run_all_tests():
    # Initialize database tables first
    initialize_db()

    test_youtube_search()
    test_audio_download()
    test_database_functions()
    print("All tests passed!")

if __name__ == "__main__":
    run_all_tests()
