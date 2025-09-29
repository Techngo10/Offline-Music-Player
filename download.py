import os
import yt_dlp


def search_youtube(query, max_results=5):
    """Search YouTube and return a list of video info dicts."""
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'default_search': f'ytsearch{max_results}',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        search_results = ydl.extract_info(query, download=False)
        return search_results['entries']


def download_youtube_audio(video_url, user="default_user", output_dir="downloads"):
    """Download YouTube video audio + cover art as MP3."""
    user_folder = os.path.join(output_dir, user)
    os.makedirs(user_folder, exist_ok=True)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(user_folder, '%(title)s [%(id)s].%(ext)s'),
        'postprocessors': [
            {  # Convert to MP3
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },
            {  # Download and embed thumbnail into MP3
                'key': 'EmbedThumbnail',
            },
            {  # Write metadata (title, artist, etc.)
                'key': 'FFmpegMetadata',
            }
        ],
        'writethumbnail': True,  # saves thumbnail as jpg too
        'quiet': False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=True)
        filename = ydl.prepare_filename(info_dict)
        mp3_file = os.path.splitext(filename)[0] + ".mp3"

    return mp3_file, info_dict.get("thumbnail", None)


if __name__ == "__main__":
    query = input("Enter song title: ")
    results = search_youtube(query)

    # Show results to user
    print("\nSearch Results:")
    for idx, video in enumerate(results, start=1):
        print(f"{idx}. {video['title']} ({video.get('duration_string', 'N/A')}) - {video.get('uploader', 'Unknown')}")

    choice = int(input("\nSelect the number of the video to download: ")) - 1
    selected_video = results[choice]

    filepath, thumb_url = download_youtube_audio(selected_video['webpage_url'], user="test_user")
    print(f"\nDownloaded: {filepath}")
    print(f"Cover art: {thumb_url}")
