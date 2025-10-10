import os
import sqlite3
import yt_dlp

DB_FILE = "musicApp.db"
DOWNLOAD_DIR = "downloads"
MAX_RESULTS = 5

# ----------------- Database function -----------------
def add_song_to_db(db_file, song_name, artist_name=None, album_name=None, lyrics=None, length=None, file_path=None, cover_art=None):
    """Add a song to songsDownloaded table and return song_id."""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO songsDownloaded (song_name, artist_name, album_name, lyrics, length, file_path, cover_art)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (song_name, artist_name, album_name, lyrics, length, file_path, cover_art))
    
    song_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return song_id

# ----------------- YouTube functions -----------------
def search_youtube(query, max_results=MAX_RESULTS):
    """Search YouTube and return a list of video info dicts."""
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'default_search': f'ytsearch{max_results}',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        search_results = ydl.extract_info(query, download=False)
        return search_results['entries']

def download_youtube_audio(video_url, user="default_user", output_dir=DOWNLOAD_DIR):
    """Download YouTube video audio + cover art as MP3 and return metadata."""
    user_folder = os.path.join(output_dir, user)
    os.makedirs(user_folder, exist_ok=True)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(user_folder, '%(title)s [%(id)s].%(ext)s'),
        'postprocessors': [
            {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'},
            {'key': 'EmbedThumbnail'},
            {'key': 'FFmpegMetadata'}
        ],
        'writethumbnail': True,
        'quiet': False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=True)
        filename = ydl.prepare_filename(info_dict)
        mp3_file = os.path.splitext(filename)[0] + ".mp3"

    metadata = {
        'song_name': info_dict.get('title'),
        'artist_name': info_dict.get('uploader'),
        'length': info_dict.get('duration'),  # in seconds
        'cover_art': info_dict.get('thumbnail'),
        'file_path': mp3_file,
    }

    return metadata

def download_and_save_song(db_file, video_url, user="default_user"):
    """Download song from YouTube and save metadata in database."""
    metadata = download_youtube_audio(video_url, user=user)
    
    song_id = add_song_to_db(
        db_file,
        song_name=metadata['song_name'],
        artist_name=metadata['artist_name'],
        length=metadata['length'],
        file_path=metadata['file_path'],
        cover_art=metadata['cover_art']
    )
    
    return song_id, metadata

# ----------------- Main program -----------------
if __name__ == "__main__":
    # Ask for user info
    username = input("Enter your username (for user-specific folder): ").strip()
    
    query = input("Enter song title to search on YouTube: ").strip()
    results = search_youtube(query)

    # Show search results
    print("\nSearch Results:")
    for idx, video in enumerate(results, start=1):
        print(f"{idx}. {video['title']} ({video.get('duration_string', 'N/A')}) - {video.get('uploader', 'Unknown')}")

    choice = int(input("\nSelect the number of the video to download: ")) - 1
    selected_video = results[choice]

    # Download and save
    song_id, metadata = download_and_save_song(DB_FILE, selected_video['webpage_url'], user=username)
    
    print(f"\nDownloaded '{metadata['song_name']}' by {metadata['artist_name']}")
    print(f"Saved at: {metadata['file_path']}")
    print(f"Cover art URL: {metadata['cover_art']}")
    print(f"Song ID in database: {song_id}")
