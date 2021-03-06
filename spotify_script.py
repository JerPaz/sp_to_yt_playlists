from unicodedata import category
import config
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from pytube import Search

def main():
    auth_manager = SpotifyClientCredentials(config.SPOTIPY_CLIENT_ID, config.SPOTIPY_CLIENT_SECRET)
    sp = spotipy.Spotify(auth_manager=auth_manager)
    playlists = sp.user_playlists(config.USER_ID)
    playlists_names_id_dict = {}
    all_playlists_name_tracks_dict = {}

    for i in range(len(playlists['items'])):
        curr_playlist = playlists['items'][i]
        playlists_names_id_dict[curr_playlist['name']] = curr_playlist['id']
        all_playlists_name_tracks_dict[curr_playlist['name']] = []
    print(all_playlists_name_tracks_dict)

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
            album = curr_playlist_tracks[i]['track']['album']['name']
            all_playlists_name_tracks_dict[key].append([song, artist, album])
    return all_playlists_name_tracks_dict

# Only for single playlist
def spot_playlist_tracks(spotify_playlist_name, in_all_playlists_name_tracks_dict, num_songs):
    all_playlists_name_tracks_dict = in_all_playlists_name_tracks_dict

    spot_all_playlists_name_tracks_dict = all_playlists_name_tracks_dict
    single_playlist_dict = {'playlist_title': spotify_playlist_name, 'items': []}

    print('num songs= {}'.format(num_songs))
    index = 0
    while index < num_songs:
        try:
            song = spot_all_playlists_name_tracks_dict[spotify_playlist_name][index][0]
        except Exception as e:
            print("CANNOT FIND PLAYLIST // Exception e: {}".format(e))
        artist = spot_all_playlists_name_tracks_dict[spotify_playlist_name][index][1]
        album = spot_all_playlists_name_tracks_dict[spotify_playlist_name][index][2]
        ost_key_words = ['OST', 'Original TV Soundtrack', 'Original Television Soundtrack']
        if any(x in album for x in ost_key_words):
            s = Search('{} {} MV'.format(song, artist))
        else:
            s = Search('{} {}'.format(song, artist))
        first_result = s.results[0]
        if 'lyrics' in first_result.title.lower():
            first_result = s.results[1]
        yt_video_url = first_result.watch_url
        video_id = yt_video_url[yt_video_url.find('v=')+2:]
        print("Song Num/Loc: {}, Video ID: {}, YT URL: {}".format(
            index, video_id, yt_video_url))
        single_playlist_dict['items'].append({'song': song, 
                                    'artist': artist,
                                    'yt_video_url': yt_video_url,
                                    'video_id': video_id,})
        index+=1
    return single_playlist_dict
