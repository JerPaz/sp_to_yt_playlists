import spotify_script
import yt_script
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

def main():
    in_single_spotify_playlist = spotify_script.spot_playlist_tracks('K-Music', 
        spot_all_playlists_name_tracks_dict, len(spot_all_playlists_name_tracks_dict['K-Music']))

    youtube = login_authenticate()

    spotify_playlists_dict = {}
    spotify_playlists_dict[in_single_spotify_playlist['playlist_title']] = in_single_spotify_playlist
    print(in_single_spotify_playlist)

    yt_existing_playlists = yt_script.get_existing_playlists(spotify_playlists_dict, youtube)
    yt_playlist = yt_script.create_playlist(in_single_spotify_playlist, yt_existing_playlists, youtube)
    yt_script.insert_tracks(yt_playlist, youtube)

# TODO change authentication so as not to login every time
def login_authenticate():
    flow = InstalledAppFlow.from_client_secrets_file(
        "client_secrets.json", 
        scopes=["https://www.googleapis.com/auth/youtube.force-ssl"])
    flow.run_local_server(port=8080, prompt='consent')
    credentials = flow.credentials
    youtube = build("youtube", "v3", credentials=credentials)
    return youtube

if __name__ == '__main__':
    spot_all_playlists_name_tracks_dict = spotify_script.main()
    main()
