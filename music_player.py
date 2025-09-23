import pygame, random

class MusicPlayer:
    def __init__(self, playlist):
        pygame.mixer.init()
        self.playlist = playlist
        self.current_index = 0
        self.loop = False
        self.shuffle = False

    def play(self, song=None):
        ## If no song is loaded, play the current song in the playlist
        ## If a song is loaded, play the current song
        if song is None:
            song = self.playlist[self.current_index]
        
        try:
            current_song = pygame.mixer.music.get_pos()
        except pygame.error:
            current_song = -1

        if pygame.mixer.music.get_busy() == 0 and current_song != -1:
            pygame.mixer.music.unpause()
            print(f"Resuming: {song}")
        else:
            pygame.mixer.music.load(song)
            pygame.mixer.music.play(-1 if self.loop else 0)
            print(f"Now playing: {song}")

    def pause(self):
        pygame.mixer.music.pause()
        print(f"Paused: {self.playlist[self.current_index]}")

    def next_song(self):
        if self.shuffle:
            self.current_index = random.randint(0, len(self.playlist)-1)
        else:
            self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play()

    ## Functionality below needs to be tested with more songs to prove it works as intended...
    def previous_song(self):
        if self.shuffle:
            self.current_index = random.randint(0, len(self.playlist)-1)
        else:
            self.current_index = (self.current_index - 1) % len(self.playlist)
        self.play()

    def toggle_loop(self):
        self.loop = not self.loop
        print(f"Looping is now {'enabled' if self.loop else 'disabled'}.")

    ## Shuffle Doesn't Work as Intended, might need more songs to actually test...
    def toggle_shuffle(self):
        self.shuffle = not self.shuffle
        print(f"Shuffle is now {'enabled' if self.shuffle else 'disabled'}.")