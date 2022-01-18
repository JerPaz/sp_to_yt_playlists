import config
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

auth_manager = SpotifyClientCredentials(config.SPOTIPY_CLIENT_ID, config.SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)

playlists = sp.user_playlists(config.USER_ID)

playlists_names_id_dict = {}
all_playlists_name_tracks_dict = {}

for i in range(len(playlists['items'])):
    curr_playlist = playlists['items'][i]
    playlists_names_id_dict[curr_playlist['name']] = curr_playlist['id']
    all_playlists_name_tracks_dict[curr_playlist['name']] = []

# Very slightly modified, but humongous credit to this stack overflow post: 
# https://stackoverflow.com/questions/39086287/spotipy-how-to-read-more-than-100-tracks-from-a-playlist
def get_playlist_tracks(playlist_id):
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

for key, value in all_playlists_name_tracks_dict.items():
    curr_playlist_tracks = get_playlist_tracks(playlists_names_id_dict[key])
    for i in range(len(curr_playlist_tracks)):
        song = curr_playlist_tracks[i]['track']['name']
        song_id = curr_playlist_tracks[i]['track']['name']
        artist = curr_playlist_tracks[i]['track']['artists'][0]['name']
        artist_id = curr_playlist_tracks[i]['track']['artists'][0]['uri']
        all_playlists_name_tracks_dict[key].append([song, artist])