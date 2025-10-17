#This file creates the database for the music player system
import sqlite3

# Create User table
conn = sqlite3.connect("musicApp.db") #these few lines create the musicApp database which everything is stored in for the music player app
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS current_user ( #current use tracks who is currently logged in
        user_id INTEGER UNIQUE,
        FOREIGN KEY(user_id) REFERENCES users(user_id) #points to the user_id in the users table
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS users ( #creates a users table, this is to store each of the details of the user and then be able to access them
    user_id INTEGER PRIMARY KEY AUTOINCREMENT, #unique id made for each user created
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    username TEXT UNIQUE,
    password TEXT,
    phone_no INTEGER,
    profile_pic TEXT #stores the address of where the image file is stored
    )
    """)

# Create songs downloaded table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS songsDownloaded ( #this is a table of all the songs that have been downloaded into the system
    song_id INTEGER PRIMARY KEY AUTOINCREMENT, #have a unique id so that each song can be easily referenced in other tables and easily accessed
    artist_name TEXT,
    song_name TEXT,
    album_name TEXT,
    lyrics TEXT,
    length REAL,
    file_path TEXT,
    cover_art TEXT
    )
    """)

# Create playlist table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS playlist ( #playlist table, which stores the details of each playlist that is created
    playlist_id INTEGER PRIMARY KEY AUTOINCREMENT, #unique id for each playlist which can be used to reference a specific playlist
    playlist_name TEXT,
    cover_photo TEXT,
    user_id INTEGER,
    FOREIGN KEY(user_id) REFERENCES users(user_id) #foreign key says that the user_id value in this table is pointing to the user_id in the users table
    #this is so that it knows which user the playlist belongs to, so when it's being displayed, it show's just the ones for the current user
    )
    """)


# create playlist songs table 
cursor.execute("""
    CREATE TABLE IF NOT EXISTS playlist_songs ( #this table stores the references for the songs that are in playlists, and which playlists they are in
    playlist_id INTEGER, //have a foreign key to the playlist table and the id stored in there so that the with the song_id in this table it can be seen which song belongs to which playlist
    song_id INTEGER, #also a foriegn key to the information stored in the songsdownloaded table, so that it can get the song information and not have it stored in this table where it isn't relevant
    PRIMARY KEY (playlist_id, song_id), #this is the primary key, which basically says that the id of the playlist and songs is what is in the playlist
    FOREIGN KEY(playlist_id) REFERENCES playlist(playlist_id),
    FOREIGN KEY(song_id) REFERENCES songsDownloaded(song_id)
    )
    """)


conn.commit()
conn.close()
