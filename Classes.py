import sqlite3


class Account: #the account class contains all the functions for regarding the account details
    # put what is inside Account here
    def login(db_file, input_username, input_password): #this function takes the database and the user's input and finds if the password is 
        #correct and if so, it sets the user_id to the curr_user (current user)
        #put function implementation here
        conn = sqlite3.connect(db_file) #connect to the database
        cursor = conn.cursor()

        #from database get the user id and the password from the users table for the input that was entered
        cursor.execute("""SELECT user_id, password FROM users WHERE username = ?""", (input_username,))
        result = cursor.fetchone()

        if result is None:
            # Username not found
            conn.close()
            return None, "Username or password is incorrect. Do you want to create an account?"
            #go to create account if yes (add later as an extention if time)

        user_id, stored_password = result
         
        
        if stored_password == input_password: #if the entered password is the password in the database for the username
            #update currUser
            conn.close()
            return User(db_file, user_id), "Login successful!" #now logged in
                #returns a user instance to then say who currUser is
        else:
            conn.close()
            return None, "Username or password is incorrect."

        

    def createNewAccount(db_file, firstName, lastName, email, username, password): #create a new account with the input details
        #put function implementation here
        conn = sqlite3.connect(db_file) #access database 
        cursor = conn.cursor()

        cursor.execute("""INSERT INTO users (first_name, last_name, email, username, password) VALUES (?, ? , ?, ?, ?)""", (firstName, lastName, email, username, password,)) #put each value in database tables - new entries
        
        cursor.execute("""SELECT last_insert_rowid()""")
        newUserID = cursor.fetchone()[0]
           
        conn.commit()
        conn.close()
        #now logged in
        return User(db_file, newUserID), "Account created"
    

class User(Account): #this class contains the functions for relating to the user
    def __init__(self, db_file, userID): //so that we can be referencing these basic things that it needs easily
        self.db_file = db_file
        self.user_id = userID #this updates to the userID of whoever is logged in

    # put what is inside User here
    def logout(self): #logsout current user by setting the current user to 0
        #put function implementation here
        #go to logged out page, remove current user
        currUser = 0 #not a valid number therefore no one is logged in
        return 0 #no one is logged in anymore
        

    def viewPlaylists(self): #goes into the database and finds the playlists for the current user and returns them all
        #put function implementation here
        #list the playlists
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        cursor.execute("""SELECT playlist_id, playlist_name FROM playlist WHERE user_id = ?""", (self.user_id,))
        result = cursor.fetchall()
        
        #print(result)
        conn.close()

        return result
        
        
    def createNew(self, firstSong): #this creates a new playlist with the user's id and the selected song's id
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


    def changeProfilePic(self, newPic): #this takes the new photos path and replaces it in the database from the old one/puts it in for start
        #put function implementation here
        #to add or change their pfp
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute("UPDATE users SET profile_pic = ? WHERE user_id = ?",(newPic, self.user_id,))
    
        conn.commit()
        conn.close()
        return True, "new profile pic updated!"
        
    def addOrChangePhone(self, phoneNo): #possible extension function that I wrote anyway, but like isn't integral to the app's functionality
        #it just takes an entered phone number and puts it in the database for the user id
        #put function implementation here
        #because it's optional to add, and don't at the sign up
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        cursor.execute("UPDATE users SET phone_no = ? WHERE user_id = ?",(phoneNo, self.user_id,))
    
        conn.commit()
        conn.close()
        return True, "phone no. saved"


    
class Playlist(): #this class contains the functionality to do with the playlists
    # put what is inside Playlist here
    def __init__(self, db_file, playlist_id): #so can reference the current playlist id easier
        self.db_file = db_file
        self.playlist_id = playlist_id

    def addSong(self, selectedSong): //adds a selected song to selected playlist by using the ids and puts it into the database
        #put function implementation here
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        cursor.execute("""INSERT INTO playlist_songs (playlist_id, song_id) VALUES (?,?)""", (self.playlist_id, selectedSong,))
    
        conn.commit()
        conn.close()
        return True, "song added"

    def removeSong(self, targetSong): #takes the chosen song and the current playlist and finds the occurence of it in the playlist in the database and removes it
        #put function implementation here
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        cursor.execute("""DELETE FROM playlist_songs WHERE song_id == ? AND playlist_id == ?""", (targetSong, self.playlist_id,))
    
        conn.commit()
        conn.close()
        return True, "song removed"


    def changePlaylistName(self, newPlaylistName): #takes input and changes the chosen playlists name to that input with the database
        #put function implementation here
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        cursor.execute("""UPDATE playlist set playlist_name = ? WHERE playlist_id = ?""", (newPlaylistName, self.playlist_id,))
    
        conn.commit()
        conn.close()
        return True, "playlist name changed"


    def deletePlaylist(self): #deletes the chosen playlist completely from the database, which means everything contained within it too like the song ids, but not that actual songs to be clear
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


    def uploadCover(self, coverImage): #takes the path to the cover image and inserts it into the database for the user id so that will be accessed to display it in the gui
        #put function implementation here
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        cursor.execute("""UPDATE playlist SET cover_photo = ? WHERE playlist_id = ?""",(coverImage, self.playlist_id,))

        conn.commit()
        conn.close()
        return True, "Cover image uploaded!"


    def removeCover(self): #deletes cover in the current playlist in the database
        #put function implementation here
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        cursor.execute("""UPDATE playlist  SET cover_photo = NULL WHERE playlist_id = ?""",(self.playlist_id,))
    
        conn.commit()
        conn.close()
        return True, "song removed"


    
    def viewSongs(self): #this takes the playlist and finds all the details for each of the songs in the database for that playlist and returns them, by using the playlist id, and then those can be displayed
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        cursor.execute(""" SELECT s.song_id, s.song_name, s.artist_name, s.album_name, s.length FROM playlist_songs ps JOIN songsDownloaded s ON ps.song_id = s.song_id WHERE ps.playlist_id = ?""", (self.playlist_id,))
        songs = cursor.fetchall()
        
        conn.close()

        return songs
