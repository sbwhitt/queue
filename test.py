import spotipy
import json
import spotipy.util as util
from config import *

scopes = 'user-read-playback-state user-modify-playback-state playlist-read-collaborative playlist-read-private playlist-modify-private'
username = 'sbw978-us'
laptop_id = DEVICES['laptop']
phone_id = DEVICES['phone']
token = util.prompt_for_user_token(username, scopes, client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, 
    redirect_uri=SPOTIPY_REDIRECT_URI)
spot = spotipy.Spotify(auth=token)

def play_music(self):
    self.spot.start_playback(device_id=self.phone_id)

def pause_music(self):
    self.spot.pause_playback(device_id=self.phone_id)

def get_playback(self):
    return self.spot.current_playback()

def queue_track(self, sid):
    self.spot.add_to_queue(sid)

def search_track(self, title):
    return self.spot.search(title, type='track')['tracks']['items'][0]['id']
