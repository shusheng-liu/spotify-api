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
        print(f"Transferred {counter} songs into song history playlist...")      

    print("Done transferring!")
    
def create_recently_played_songs(user_id):
     # create playlist to put songs into
    playlist_information = sp.user_playlist_create(user=user_id, name='recent jams', public=True, description="25 of the most recently liked songs and 25 of the top tracks this month.")
    playlist_id = playlist_information['id']
    # obtain first 20 saved tracks
    saved_tracks = sp.current_user_saved_tracks(limit=20)  
    amount_of_tracks = len(saved_tracks['items'])
    # iterate and obtain track url for the current list of saved tracks
    tracks = []
    for i in range(amount_of_tracks):
        track_uri = saved_tracks['items'][i]['track']['uri']
        tracks.append(track_uri)
    
    # obtain top 30 most played tracks
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
    # obtain saved track playlist id
    more_playlists = True
    counter = 0
    playlists = sp.current_user_playlists(offset=counter)
    playlist_id = None
    # iterate through current user's playlist
    while more_playlists:
        more_playlists = playlists['next'] is not None
        amount_of_playlists = len(playlists['items'])
        # if playlist name is "song history" update playlist_id and break from loop
        for i in range(amount_of_playlists):
            if (playlists['items'][i]['name'] == 'song history'):
                playlist_id = playlists['items'][i]['id']
                more_playlists = False
                break
        counter += amount_of_playlists
        playlists = sp.current_user_playlists(offset=counter)
        
    # if after all user's playlist is searched and not found throw error.    
    if playlist_id is None:
        raise Exception("Playlist not found.")
        
    # Get the latest song that was updated into saved track playlist
    no_more_updates = False
    most_recent_track = sp.playlist_tracks(limit=1, playlist_id=playlist_id, fields='items(track(uri))')
    most_recent_track = most_recent_track['items'][0]['track']['uri']
    counter = 0
    print(f"Target: {most_recent_track}")
    
    # get latest saved tracks and check if current track has been saved
    while not no_more_updates:
        saved_tracks = sp.current_user_saved_tracks(limit=50, offset=counter)
        amount_of_tracks = len(saved_tracks['items'])
        tracks = []
        for i in range(amount_of_tracks):
            track_uri = saved_tracks['items'][i]['track']['uri']
            print(f"current track: {track_uri}")
            # if current track is the most recent track, we have finished updating
            if (track_uri == most_recent_track):
                no_more_updates = True
                break
            tracks.append(track_uri)
        # append all the tracks that are not yet in the playlist
        if not tracks:
            print("No songs to update")
            return
        sp.playlist_add_items(playlist_id=playlist_id, items=tracks, position=counter)
        counter += amount_of_tracks
                
    print("Updated song history playlist")

def update_most_played_playlist():
    # get playlist id
    more_playlists = True
    counter = 0
    playlists = sp.current_user_playlists(offset=counter)
    playlist_id = None
    # iterate through current user's playlist
    while more_playlists:
        more_playlists = playlists['next'] is not None
        amount_of_playlists = len(playlists['items'])
        # if playlist name is "recent jams" update playlist_id and break from loop
        for i in range(amount_of_playlists):
            if (playlists['items'][i]['name'] == 'recent jams'):
                playlist_id = playlists['items'][i]['id']
                more_playlists = False
                break
        counter += amount_of_playlists
        playlists = sp.current_user_playlists(offset=counter)
        
    if playlist_id is None:
        raise Exception("Playlist not found.")
    
    deleted_songs = sp.playlist_tracks(limit=50, playlist_id=playlist_id, fields='items(track(uri))')
    deleted_songs_uri = []
    for items in deleted_songs['items']:
        deleted_songs_uri.append(items['track']['uri'])
        
    sp.playlist_remove_all_occurrences_of_items(playlist_id=playlist_id, items=deleted_songs_uri)
    print("Deleting all songs in recent jam playlist.")
    
    # obtain first 20 saved tracks
    saved_tracks = sp.current_user_saved_tracks(limit=20)  
    amount_of_tracks = len(saved_tracks['items'])
    # iterate and obtain track url for the current list of saved tracks
    tracks = []
    for i in range(amount_of_tracks):
        track_uri = saved_tracks['items'][i]['track']['uri']
        tracks.append(track_uri)    
        
    # obtain top 30 played tracks
    top_played_tracks = sp.current_user_top_tracks(limit=30, time_range='short_term')  
    amount_of_tracks = len(top_played_tracks['items'])
    # iterate and obtain track url for the current list of saved tracks
    for i in range(amount_of_tracks):
        track_uri = top_played_tracks['items'][i]['uri']
        if track_uri not in tracks:
            tracks.append(track_uri)
    # put found track uri's into created playlist, with songs currently found at bottom
    sp.playlist_add_items(playlist_id=playlist_id, items=tracks)
    
    print("Done updating recent jam playlist!")
    

if __name__ == "__main__":
    update_saved_track_playlist()
    update_most_played_playlist()
    