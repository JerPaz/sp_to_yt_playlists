import re
from tabnanny import check
from urllib import request
from xmlrpc.client import Boolean
from os import name

def get_existing_playlists(in_spotify_playlists_dict, youtube_obj):
    spotify_playlists_dict = in_spotify_playlists_dict
    youtube = youtube_obj
    exisiting_playlists = {}

    request_playlist_list = youtube.playlists().list(
        part="snippet, contentDetails", 
        maxResults=10, 
        mine=True)
    response_obj = request_playlist_list.execute()

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

#existing_playlists = get_existing_playlists()

# TODO update exisiting playlist values once tracks are inserted into playlist
# TODO change public/private settings to unlisted for playlists

def create_playlist(spot_playlist, in_existing_playlists, youtube_obj):
    existing_playlists = in_existing_playlists
    youtube = youtube_obj
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


#create_playlist(k_music_spotify_playlist)
#k_music_yt_playlist = create_playlist(k_music_spotify_playlist)
#existing_playlists[k_music_yt_playlist['title']] = (k_music_yt_playlist)

def insert_tracks(yt_playlist, youtube_obj):
    youtube = youtube_obj
    request_item_list = youtube.playlistItems().list(
        part='id',
        playlistId = yt_playlist['id']
    )
    response_item_list = request_item_list.execute()
    exisiting_tracks_id_only = []
    curr_num_items = response_item_list['pageInfo']['totalResults']
    if curr_num_items < len(yt_playlist['spotify_playlist']['items']):
        i = curr_num_items
        while i < len(yt_playlist['spotify_playlist']['items']):
            yt_playlist_id = yt_playlist['id']
            yt_video_id = yt_playlist['spotify_playlist']['items'][i]['video_id']
            if yt_video_id not in exisiting_tracks_id_only:
                print("Song Inserted: {}, Video ID: {}".format(yt_playlist['spotify_playlist']['items'][i]['song'], 
                    yt_playlist['spotify_playlist']['items'][i]['video_id']))
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

#insert_tracks(existing_playlists['K-Music'])

def delete_playlist(yt_playlist, youtube_obj):
    youtube = youtube_obj
    request = youtube.playlistItems().delete(
        id=yt_playlist['id']
    )
    request.execute()