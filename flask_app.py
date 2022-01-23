import os
import config
import requests
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
    return redirect("/user")

def protect_user_page(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)
        else:
            return function()
    return wrapper

@app.route("/user")
@protect_user_page
def user_area():
    return "<h1>User area: {}</h1>".format(session["google_id"])

@app.route("/logout")
def logout():
    session.clear()
    flash('You were logged out', 'alert-success')
    return redirect('/home')

if __name__ == '__main__':
    app.run(debug=True)