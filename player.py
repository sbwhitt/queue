import spotipy
import json
import time
import spotipy.util as util
from config import *
from threading import Thread

MASTER_NAME = PLAYLIST_NAME

class player(Thread):
    def __init__(self):
        Thread.__init__(self)
        scopes = 'user-read-playback-state user-modify-playback-state playlist-read-collaborative playlist-read-private playlist-modify-private'

        token = util.prompt_for_user_token(USER, scopes, client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, 
            redirect_uri=SPOTIPY_REDIRECT_URI)
        self.spot = spotipy.Spotify(auth=token)

        self.device_id = ''
        self.master = self._get_master_playlist()
        self.master_tracks = self.spot.user_playlist_tracks(USER, playlist_id=self.master['uri'])
        self.position = 0
        self.current_track = self.master_tracks['items'][self.position]
        self.start_time = 0
        self.progress = 0
        self.playing = True
        self.paused = False
        self.pause_time = 0

    def _get_master_playlist(self):
        offset = 0
        playlists = self.spot.current_user_playlists(limit=50, offset=offset)
        while playlists['items']:
            for p in playlists['items']:
                if p['name'] == MASTER_NAME:
                    return p
            offset += 50
            playlists = self.spot.current_user_playlists(limit=50, offset=offset)
        return None
    
    def select_device(self):
        devices = self.spot.devices()
        for d in devices['devices']:
            print(d['name'])
        
        device_id = devices['devices'][int(input('select device: '))]['id']
        self.device_id = device_id

    def start_track(self):
        self.spot.start_playback(context_uri=self.master['uri'], offset={'position' : self.position}, device_id=self.device_id)
        self.start_time = time.time()

    def run(self):
        while self.playing:
            if not self.paused:
                current = self.master_tracks['items'][self.position]
                self.current_track = current['track']
                progress = int(1000*(time.time() - self.start_time)) + 400
                self.progress = progress
                if abs(progress - self.current_track['duration_ms']) < 1000:
                    self.position += 1
                    self.start_track()
            print(json.dumps(self.current_track['name'], indent=4))
            print(str(int(progress/1000)) + " | " + str(int(self.current_track['duration_ms']/1000)))
            print()
            time.sleep(1)
    
    def stop(self):
        self.playing = False
    
    def pause_track(self):
        self.paused = True
        self.spot.pause_playback()
        self.pause_time = time.time()
    
    def resume_track(self):
        self.paused = False
        self.spot.start_playback(context_uri=self.master['uri'], offset={'position' : self.position})
        time_paused = time.time() - self.pause_time
        self.start_time += time_paused
        self.spot.seek_track(self.progress)

    def next_track(self):
        self.paused = False
        self.position += 1
        self.progress = 0
        self.start_track()
    
    def synchronize(self):
        self.spot.start_playback(context_uri=self.master['uri'], offset={'position' : self.position})
        self.spot.seek_track(self.progress)
    
    def pause_music(self):
        self.spot.pause_playback()

if __name__ == "__main__":
    p = player()

    p.select_device()
    
    p.start_track()
    p.start()

    inp = ''
    while inp != 'q':
        inp = input()
        if inp == 's':
            p.synchronize()
        elif inp == 'n':
            p.next_track()
        elif inp == 'p':
            p.pause_track()
        elif inp == 'r':
            p.resume_track()

    print("exiting")
    
    p.stop()
    p.pause_music()
