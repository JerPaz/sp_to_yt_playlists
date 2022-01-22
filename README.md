Transfering Playlists from SPOT to YT
=====================================

Small and light script/program used to convert Spotify playlists into YouTube playlists

Package requirements:
---------------------
1. Spotipy
2. Pytube
3. Google API Python Client
4. Google Auth OAuthLib

Need to create a config.py file with the following info:
--------------------------------------------------------
1. USER_ID (spotify username)
2. SPOTIPY_CLIENT_ID (found on the Spotify web dev dashboard)
3. SPOTIPY_CLIENT_SECRET (also found on the Spotify web dev dashboard, be careful with this)

Need to obtain a JSON file with client information:
---------------------------------------------------
* Found on the Google Cloud Platform API Console after creating a project
