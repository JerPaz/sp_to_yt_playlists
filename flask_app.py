import os
import config
import requests
import spotify_script
import yt_script
from os import abort
from flask import Flask, session, render_template, redirect, request, flash
from google.oauth2 import id_token
from google_auth_oauthlib.flow import InstalledAppFlow
import google.auth.transport.requests as google_requests
from googleapiclient.discovery import build
from cachecontrol import CacheControl

app = Flask(__name__)
app.secret_key = config.BACKEND_CLIENT_SECRET
flow = InstalledAppFlow.from_client_secrets_file(
            'client_secrets.json',
            scopes=[
                'https://www.googleapis.com/auth/youtube.force-ssl', 'openid'
            ],
            redirect_uri="http://127.0.0.1:5000/callback"
        )
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

def create_yt_playlist(youtube, in_playlist, in_num_songs):
    print('Playlist selected: {}'.format(in_playlist))
    spot_all_playlists_name_tracks_dict = spotify_script.main()
    in_single_spotify_playlist = spotify_script.spot_playlist_tracks(in_playlist, 
        spot_all_playlists_name_tracks_dict, in_num_songs)
    spotify_playlists_dict = {}
    spotify_playlists_dict[in_single_spotify_playlist['playlist_title']] = in_single_spotify_playlist
    print(in_single_spotify_playlist)

    yt_existing_playlists = yt_script.get_existing_playlists(spotify_playlists_dict, youtube)
    yt_playlist = yt_script.create_playlist(in_single_spotify_playlist, yt_existing_playlists, youtube)
    yt_script.insert_tracks(yt_playlist, youtube)

@app.route("/")
def home():
    return render_template("/home.html")

@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)
    if not session["state"] == request.args["state"]:
        abort(500)
    credentials = flow.credentials
    cached_session = CacheControl(requests.session())
    id_info = id_token.verify_oauth2_token(credentials._id_token, 
        google_requests.Request(session=cached_session), audience=config.GOOGLE_CLIENT_ID)
    session["google_id"] = id_info.get("sub")
    flash('Login Success', 'alert-success')
    return redirect("/user")

def protect_user_page(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)
        else:
            return function()
    return wrapper

@app.route("/user", methods=['GET', 'POST'])
@protect_user_page
def user_area():
    if request.method == 'POST':
        # TODO add logic to check for valid playlist and song
        # TODO make user page look nicer after adding functionality
        session["playlist_name"] = request.form['playlist_name']
        session["num_songs"] = int(request.form['num_songs'])
        return redirect("/build_yt")
    return render_template('/user.html', google_id=session['google_id'])

@app.route("/build_yt")
def build_yt():
    # TODO used passed in playlist and num songs to create a build object
    return "<h1>Built YOUTUBE successfully :)</h1>"

@app.route("/logout")
def logout():
    session.clear()
    print("cleared")
    flash('You were logged out', 'alert-success')
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)