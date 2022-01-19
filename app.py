import re
from tabnanny import check
import spotify_script
from os import name
from pytube import YouTube, Playlist, Search
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

spot_playlists_names_id_dict = spotify_script.playlists_names_id_dict
spot_all_playlists_name_tracks_dict = spotify_script.all_playlists_name_tracks_dict

# Only for single playlist
# TODO after testing, change from limit of 5 to all songs in playlist
# TODO also after testing, change from single to all playlist (maybe?)
def spot_playlist_tracks(spotify_playlist_name):
    single_playlist_dict = {}

    index = 0
    while index < 5:
        song = spot_all_playlists_name_tracks_dict[spotify_playlist_name][index][0]
        artist = spot_all_playlists_name_tracks_dict[spotify_playlist_name][index][1]
        s = Search('{} {}'.format(song, artist))
        first_result = s.results[0]
        yt_video_url = first_result.watch_url
        video_id = yt_video_url[yt_video_url.find('v=')+2:]
        print(video_id)
        print(yt_video_url)
        single_playlist_dict[spotify_playlist_name] = {'song': song, 
                                                       'artist': artist,
                                                       'yt_video_url': yt_video_url,
                                                       'video_id': video_id}
        index+=1
    
    return single_playlist_dict

k_music_playlist = spot_playlist_tracks('K-Music')

# TODO change authentication so as not to login everytime
flow = InstalledAppFlow.from_client_secrets_file(
    "client_secrets.json", 
    scopes=["https://www.googleapis.com/auth/youtube.force-ssl"])
flow.run_local_server(port=8080, prompt='consent')
credentials = flow.credentials
print(credentials.to_json())

# TODO interact with Google API to put videos in playlist
youtube = build("youtube", "v3", credentials=credentials)
request_playlist_list = youtube.playlists().list(
    part="snippet, contentDetails", 
    maxResults=5, 
    mine=True)
response_exisiting_playlists = request_playlist_list.execute()

def get_existing_playlists(response_obj):
    exisiting_playlists = {}

    for i in range(len(response_obj['items'])):
        curr_yt_existing_playlist = response_obj['items'][i]
        playlist_id = curr_yt_existing_playlist['id']
        playlist_title = curr_yt_existing_playlist['snippet']['title']
        playlist_total_videos = curr_yt_existing_playlist['contentDetails']['itemCount']
        playlist_details = {'id': playlist_id, 
                            'title': playlist_title,
                            'total_videos': playlist_total_videos}
        exisiting_playlists[playlist_title] = playlist_details
        print(playlist_id, playlist_title, playlist_total_videos)
    
    return exisiting_playlists

def check_playlist_exist(check_playlist, existing_playlists):
    if check_playlist in existing_playlists:
        return True
    else:
        return False

existing_playlists = get_existing_playlists(response_exisiting_playlists)
print(existing_playlists)
print('K-Music exist: {}'.format(check_playlist_exist('K-Music', existing_playlists)))
print('dummy_playlist: {}'.format(check_playlist_exist('dummy_playlist', existing_playlists)))

# TODO check if playlist exist, if not, then create playlist and populate it
# TODO check if playlist exist, if so, check if it has all songs; if not, then repopulate playlist with correct tracks
# TODO will require requests to insert into playlist using API playlistitems insert function


