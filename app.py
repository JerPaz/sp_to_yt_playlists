import os 
import spotify_script
import yt_script
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

def main(youtube_obj):
    in_single_spotify_playlist = spotify_script.spot_playlist_tracks('K-Music Test', 
        spot_all_playlists_name_tracks_dict, 5) #len(spot_all_playlists_name_tracks_dict['K-Music']))

    youtube = youtube_obj

    spotify_playlists_dict = {}
    spotify_playlists_dict[in_single_spotify_playlist['playlist_title']] = in_single_spotify_playlist
    print(in_single_spotify_playlist)

    yt_existing_playlists = yt_script.get_existing_playlists(spotify_playlists_dict, youtube)
    yt_playlist = yt_script.create_playlist(in_single_spotify_playlist, yt_existing_playlists, youtube)
    yt_script.insert_tracks(yt_playlist, youtube)

# All credit to Corey Schafer and his OAuth tutorial
# Taken straight from the snippet provided as no real need to change it
# Reference: https://gist.github.com/CoreyMSchafer/ea5e3129b81f47c7c38eb9c2e6ddcad7
def login_authenticate():
    credentials = None
    # token.pickle stores the user's credentials from previously successful logins
    if os.path.exists('token.pickle'):
        print('Loading Credentials From File...')
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)
    
    
    # If there are no valid credentials available, then either refresh the token or log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print('Refreshing Access Token...')
            credentials.refresh(Request())
        else:
            print('Fetching New Tokens...')
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json',
                scopes=[
                    'https://www.googleapis.com/auth/youtube.force-ssl'
                ]
            )

            flow.run_local_server(port=8080, prompt='consent',
                                authorization_prompt_message='')
            credentials = flow.credentials

            # Save the credentials for the next run
            with open('token.pickle', 'wb') as f:
                print('Saving Credentials for Future Use...')
                pickle.dump(credentials, f)

    youtube = build("youtube", "v3", credentials=credentials)
    return youtube

if __name__ == '__main__':
    spot_all_playlists_name_tracks_dict = spotify_script.main()
    main(login_authenticate())
