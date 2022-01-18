import spotify_script
from os import name
from pytube import YouTube, Playlist, Search
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

spot_playlists_names_id_dict = spotify_script.playlists_names_id_dict
spot_all_playlists_name_tracks_dict = spotify_script.all_playlists_name_tracks_dict

# Only for single playlist
# TODO after testing, change from limit of 10 to all songs in playlist
# TODO also after testing, change from single to all playlist (maybe?)
index = 0
while index < 10:
    song = spot_all_playlists_name_tracks_dict['K-Music'][index][0]
    artist = spot_all_playlists_name_tracks_dict['K-Music'][index][1]
    s = Search('{} {}'.format(song, artist))
    first_result = s.results[0]
    yt_video_url = first_result.watch_url
    video_id = yt_video_url[yt_video_url.find('v=')+2:]
    print(video_id)
    print(yt_video_url)
    index+=1
    pass

# TODO change authentication so as not to login everytime
flow = InstalledAppFlow.from_client_secrets_file(
    "client_secrets.json", 
    scopes=["https://www.googleapis.com/auth/youtube.force-ssl"])
flow.run_local_server(port=8080, prompt='consent')
credentials = flow.credentials
print(credentials.to_json())

# TODO interact with Google API to put videos in playlist
# youtube = build("youtube", "v3", developerKey=)
