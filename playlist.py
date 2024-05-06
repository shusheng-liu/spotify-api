import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

load_dotenv()
SPOTIPY_CLIENT_ID = os.environ.get('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET= os.environ.get('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.environ.get('SPOTIPY_REDIRECT_URI')
scope = 'user-library-read, playlist-modify-public, playlist-read-private, playlist-read-collaborative, user-top-read'

spotify_ouath = SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=scope
)

sp = spotipy.Spotify(auth_manager=spotify_ouath)
# get user id
profile_information = sp.current_user()
user_id = profile_information['id']

def create_playlist_from_saved_tracks(user_id):
    # create playlist to put songs into
    playlist_information = sp.user_playlist_create(user=user_id, name='song history', public=True)
    playlist_id = playlist_information['id']
    # obtain first 20 saved tracks
    saved_tracks = sp.current_user_saved_tracks(limit=50)
    counter = 0
    songs_remaining = True
    while songs_remaining:
        songs_remaining = saved_tracks['next'] is not None
        # keep track of current and total amount of songs iterated through
        amount_of_tracks = len(saved_tracks['items'])
        # iterate and obtain track url for the current list of saved tracks
        tracks = []
        for i in range(amount_of_tracks):
            track_uri = saved_tracks['items'][i]['track']['uri']
            tracks.append(track_uri)
        # put found track uri's into created playlist, with songs currently found at bottom
        sp.playlist_add_items(playlist_id=playlist_id, items=tracks, position=counter)
        counter += amount_of_tracks
        saved_tracks = sp.current_user_saved_tracks(offset=counter)      

    print("Done transferring!")
    
def create_recently_played_songs(user_id):
     # create playlist to put songs into
    playlist_information = sp.user_playlist_create(user=user_id, name='recent jams', public=True, description="25 of the most recently liked songs and 25 of the top tracks this month.")
    playlist_id = playlist_information['id']
    # obtain first 20 saved tracks
    saved_tracks = sp.current_user_saved_tracks(limit=25)  
    amount_of_tracks = len(saved_tracks['items'])
    # iterate and obtain track url for the current list of saved tracks
    tracks = []
    for i in range(amount_of_tracks):
        track_uri = saved_tracks['items'][i]['track']['uri']
        tracks.append(track_uri)
    # put found track uri's into created playlist, with songs currently found at bottom
    
    top_played_tracks = sp.current_user_top_tracks(limit=25, time_range='short_term')  
    amount_of_tracks = len(top_played_tracks['items'])
    # iterate and obtain track url for the current list of saved tracks
    for i in range(amount_of_tracks):
        track_uri = top_played_tracks['items'][i]['uri']
        if track_uri not in tracks:
            tracks.append(track_uri)
    # put found track uri's into created playlist, with songs currently found at bottom
    sp.playlist_add_items(playlist_id=playlist_id, items=tracks)
    
    print("Done creating playlist!")
    
def update_saved_track_playlist():
    more_playlists = True
    counter = 0
    playlists = sp.current_user_playlists(offset=counter)
    while more_playlists:
        more_playlists = playlists['next'] is not None
        amount_of_playlists = len(playlists['items'])
        for i in range(amount_of_playlists):
            if (playlists['items'][i]['name'] == 'song history'):
                playlist_id = playlists['items'][i]['id']
                more_playlists = False
                break
        counter += amount_of_playlists
        playlists = sp.current_user_playlists(offset=counter)
        
    no_more_updates = False
    most_recent_track = sp.playlist_tracks(limit=1, playlist_id=playlist_id, fields='items(track(uri))')
    most_recent_track = most_recent_track['items'][0]['track']['uri']
    counter = 0
    print(f"Target: {most_recent_track}")
    while not no_more_updates:
        saved_tracks = sp.current_user_saved_tracks(limit=50, offset=counter)
        amount_of_tracks = len(saved_tracks['items'])
        tracks = []
        for i in range(amount_of_tracks):
            track_uri = saved_tracks['items'][i]['track']['uri']
            print(f"current track: {track_uri}")
            if (track_uri == most_recent_track):
                no_more_updates = True
                break
            tracks.append(track_uri)
        # put found track uri's into created playlist, with songs currently found at bottom
        sp.playlist_add_items(playlist_id=playlist_id, items=tracks, position=counter)
        counter += amount_of_tracks
                
    print("Updated song history playlist")

def update_most_played_playlist():
    more_playlists = True
    counter = 0
    playlists = sp.current_user_playlists(offset=counter)
    while more_playlists:
        more_playlists = playlists['next'] is not None
        amount_of_playlists = len(playlists['items'])
        for i in range(amount_of_playlists):
            if (playlists['items'][i]['name'] == 'recent jams'):
                playlist_id = playlists['items'][i]['id']
                more_playlists = False
                break
        counter += amount_of_playlists
        playlists = sp.current_user_playlists(offset=counter)

#update_saved_track_playlist()
    
    
    
#create_playlist_from_saved_tracks(user_id)

#create_recently_played_songs(user_id)
            
# create func that puts liked songs into playlist
# create playlist based on genre

# create jam class
# creates playlist and users can add songs to it