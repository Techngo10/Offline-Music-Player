import sqlite3


class Account: 
    # put what is inside Account here
    def login(db_file, input_username, input_password):
        #put function implementation here
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        cursor.execute("""SELECT user_id, password FROM users WHERE username = ?""", (input_username,))
        result = cursor.fetchone()

        if result is None:
            # Username not found
            conn.close()
            return None, "Username or password is incorrect. Do you want to create an account?"
            #go to create account if yes

        user_id, stored_password = result
         
        
        if stored_password == input_password:
            #update currUser
            conn.close()
            return User(db_file, user_id), "Login successful!" #now logged in
                #returns a user instance to then say who currUser is
        else:
            conn.close()
            return None, "Username or password is incorrect."

        

    def createNewAccount(db_file, firstName, lastName, email, username, password):
        #put function implementation here
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        cursor.execute("""INSERT INTO users (first_name, last_name, email, username, password) VALUES (?, ? , ?, ?, ?)""", (firstName, lastName, email, username, password,)) #put each value in database tables - new entries
        
        cursor.execute("""SELECT last_insert_rowid()""")
        newUserID = cursor.fetchone()[0]
           
        conn.commit()
        conn.close()
        #now logged in
        return User(db_file, newUserID), "Account created"
    


class User(Account):
    def __init__(self, db_file, userID):
        self.db_file = db_file
        self.user_id = userID #this updates to the userID of whoever is logged in

    # put what is inside User here
    def logout(self):
        #put function implementation here
        #go to logged out page, remove current user
        currUser = 0 #not a valid number therefore no one is logged in
        return 0 #no one is logged in anymore
        

    def viewPlaylists(self):
        #put function implementation here
        #list the playlists
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        cursor.execute("""SELECT playlist_id, playlist_name FROM playlist WHERE user_id = ?""", (self.user_id,))
        result = cursor.fetchall()
        
        #print(result)
        conn.close()

        return result
        
        
    def createNew(self, firstSong): 
        #put function implementation here
        #create new playlist with name being its id
        #add firstSong to playlist
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        cursor.execute("""INSERT INTO playlist (playlist_name, user_id) VALUES (?, ?)""", ("", self.user_id,))

        cursor.execute("""SELECT last_insert_rowid()""")
        newPlaylistID = cursor.fetchone()[0]

        newName = f"New Playlist #{newPlaylistID}"
        cursor.execute("""UPDATE playlist SET playlist_name = ? WHERE playlist_id = ?""", (newName, newPlaylistID))

        cursor.execute("""INSERT INTO playlist_songs (playlist_id, song_id) VALUES (?, ?)""", (newPlaylistID, firstSong,))

        conn.commit()
        conn.close()
        return newPlaylistID


    def changeProfilePic(self, newPic):
        #put function implementation here
        #to add or change their pfp
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute("UPDATE users SET profile_pic = ? WHERE user_id = ?",(newPic, self.user_id,))
    
        conn.commit()
        conn.close()
        return True, "new profile pic updated!"
        
    def addOrChangePhone(self, phoneNo):
        #put function implementation here
        #because it's optional to add, and don't at the sign up
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        cursor.execute("UPDATE users SET phone_no = ? WHERE user_id = ?",(phoneNo, self.user_id,))
    
        conn.commit()
        conn.close()
        return True, "phone no. saved"


    
class Playlist():
    # put what is inside Playlist here
    def __init__(self, db_file, playlist_id):
        self.db_file = db_file
        self.playlist_id = playlist_id

    def addSong(self, selectedSong):
        #put function implementation here
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        cursor.execute("""INSERT INTO playlist_songs (playlist_id, song_id) VALUES (?,?)""", (self.playlist_id, selectedSong,))
    
        conn.commit()
        conn.close()
        return True, "song added"

    def removeSong(self, targetSong):
        #put function implementation here
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        cursor.execute("""DELETE FROM playlist_songs WHERE song_id == ? AND playlist_id == ?""", (targetSong, self.playlist_id,))
    
        conn.commit()
        conn.close()
        return True, "song removed"


    def changePlaylistName(self, newPlaylistName):
        #put function implementation here
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        cursor.execute("""UPDATE playlist set playlist_name = ? WHERE playlist_id = ?""", (newPlaylistName, self.playlist_id,))
    
        conn.commit()
        conn.close()
        return True, "playlist name changed"


    def deletePlaylist(self):
        #put function implementation here
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        # remove all songs linked to this playlist
        cursor.execute("DELETE FROM playlist_songs WHERE playlist_id = ?",(self.playlist_id,))
        # delete the playlist
        cursor.execute("DELETE FROM playlist WHERE playlist_id = ?",(self.playlist_id,))
    
        conn.commit()
        conn.close()
        return True, "playlist deleted"


    def uploadCover(self, coverImage):
        #put function implementation here
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        cursor.execute("""UPDATE playlist SET cover_photo = ? WHERE playlist_id = ?""",(coverImage, self.playlist_id,))

        conn.commit()
        conn.close()
        return True, "Cover image uploaded!"


    def removeCover(self):
        #put function implementation here
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        cursor.execute("""UPDATE playlist  SET cover_photo = NULL WHERE playlist_id = ?""",(self.playlist_id,))
    
        conn.commit()
        conn.close()
        return True, "song removed"


    
    def viewSongs(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        cursor.execute(""" SELECT s.song_id, s.song_name, s.artist_name, s.album_name, s.length FROM playlist_songs ps JOIN songsDownloaded s ON ps.song_id = s.song_id WHERE ps.playlist_id = ?""", (self.playlist_id,))
        songs = cursor.fetchall()
        
        conn.close()

        return songs