import re
from tabnanny import check
from urllib import request
from xmlrpc.client import Boolean
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
    single_playlist_dict = {'playlist_title': spotify_playlist_name, 'items': []}

    index = 0
    while index < 10:
        song = spot_all_playlists_name_tracks_dict[spotify_playlist_name][index][0]
        artist = spot_all_playlists_name_tracks_dict[spotify_playlist_name][index][1]
        s = Search('{} {}'.format(song, artist))
        first_result = s.results[0]
        yt_video_url = first_result.watch_url
        video_id = yt_video_url[yt_video_url.find('v=')+2:]
        print(video_id)
        print(yt_video_url)
        single_playlist_dict['items'].append({'song': song, 
                                     'artist': artist,
                                     'yt_video_url': yt_video_url,
                                     'video_id': video_id,})
        index+=1
    
    return single_playlist_dict

spotify_playlists_dict = {}
k_music_spotify_playlist = spot_playlist_tracks('K-Music')
spotify_playlists_dict[k_music_spotify_playlist['playlist_title']] = k_music_spotify_playlist
print(k_music_spotify_playlist)

# TODO change authentication so as not to login everytime
flow = InstalledAppFlow.from_client_secrets_file(
    "client_secrets.json", 
    scopes=["https://www.googleapis.com/auth/youtube.force-ssl"])
flow.run_local_server(port=8080, prompt='consent')
credentials = flow.credentials

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
                            'total_videos': playlist_total_videos,
                            'spotify_playlist': None} # THE PROBLEM IS RIGHT HERE
        if playlist_details['title'] in spotify_playlists_dict:
            playlist_details['spotify_playlist'] = spotify_playlists_dict[playlist_details['title']]
        exisiting_playlists[playlist_title] = playlist_details
        print(playlist_id, playlist_title, playlist_total_videos)
    
    return exisiting_playlists

def check_playlist_exist(check_playlist, existing_playlists):
    if check_playlist in existing_playlists:
        return True
    else:
        return False

existing_playlists = get_existing_playlists(response_exisiting_playlists)
print('K-Music exist: {}'.format(check_playlist_exist('K-Music', existing_playlists)))
print('dummy_playlist: {}'.format(check_playlist_exist('dummy_playlist', existing_playlists)))

# IT WORKS (with a huge astreik; aka as long as the playlist does not exist)
# TODO check if playlist exist, if so, check if it has all songs; if not, then repopulate playlist with correct tracks
# TODO update exisitng playlist values once tracks are inserted into playlist
# TODO change public/private settings to unlisted for playlists
# TODO make the code more readable (probably separate into separate python file and have app.py as running the functions and main calls)

def create_playlist(spot_playlist):
    playlist_name = spot_playlist['playlist_title']
    if check_playlist_exist(playlist_name, existing_playlists) == False:
        request = youtube.playlists().insert(
            part='snippet',
            body={
                'snippet': {
                'title': playlist_name
                }
            }
        )
        response = request.execute()
        return_value = {'id': response['id'], 
                        'title': response['snippet']['title'],
                        'total_videos': 0, #response['contentDetails']['itemCount'],
                        'spotify_playlist': spot_playlist}
        existing_playlists[return_value['title']] = return_value
        return return_value
    else:
        return existing_playlists[spot_playlist['playlist_title']]


create_playlist(k_music_spotify_playlist)
#k_music_yt_playlist = create_playlist(k_music_spotify_playlist)
#existing_playlists[k_music_yt_playlist['title']] = (k_music_yt_playlist)

def insert_tracks(yt_playlist):
    request_item_list = youtube.playlistItems().list(
        part='id',
        playlistId = yt_playlist['id']
    )
    response_item_list = request_item_list.execute()
    exisiting_tracks_id_only = []
    curr_num_items = response_item_list['pageInfo']['totalResults']
    # for i in range(len(response_item_list['items'])):
    #     check_against = response_item_list['items'][i]['snippet']['resourceId']['videoId']
    #     exisiting_tracks_id_only.append(check_against)
    
    print(yt_playlist['spotify_playlist']['items'])
    if curr_num_items < len(yt_playlist['spotify_playlist']['items']):
        i = curr_num_items
        while i < len(yt_playlist['spotify_playlist']['items']):
            yt_playlist_id = yt_playlist['id']
            yt_video_id = yt_playlist['spotify_playlist']['items'][i]['video_id']
            if yt_video_id not in exisiting_tracks_id_only:
                print(yt_playlist['spotify_playlist']['items'][i]['song'], 
                    yt_playlist['spotify_playlist']['items'][i]['video_id'])
                request = youtube.playlistItems().insert(
                    part="snippet",
                    body={
                        "snippet": {
                        "playlistId": yt_playlist_id,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": yt_video_id
                        }
                        }
                    }
                )
            request.execute()
            i += 1
    else:
        print("ALL TRACKS IN PLAYLIST")

insert_tracks(existing_playlists['K-Music'])

def delete_playlist(yt_playlist):
    request = youtube.playlistItems().delete(
        id=yt_playlist['id']
    )
    request.execute()

