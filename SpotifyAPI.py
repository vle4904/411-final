from requests import post, get
from flask import Flask, redirect, request, jsonify, session
from datetime import datetime, timedelta
import json
import time
import urllib.parse
import pandas as pd
import csv
from dotenv import load_dotenv
import os

load_dotenv()

#Setting up variables for usage in Spotify API
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

REDIRECT_URI = 'http://localhost:5000/callback'
AUTH_URL = 'https://accounts.spotify.com/authorize'
API_BASE_URL = 'https://api.spotify.com/v1/'
TOKEN_URL = "https://accounts.spotify.com/api/token"

#Create a flask session --> store variables/data for later access in between requests
app = Flask(__name__)
app.secret_key = '53d355f8-571a-4590-a310-1f9579440851'     #arbitrary "password"

#Welcome message for first time users
@app.route('/')
def index():
    return "Welcome to my Spotify App <a href='/login'>Login with Spotify</a> <a href='/studysession'>Start Study Session</a> <a href='/get-recommendations'>Get Recommendations</a>"

#Login endpoint --> Redirect to Spotify's Login Page
@app.route('/login')
def login():
    scope = 'user-read-private user-read-email user-read-currently-playing'     #scope parameters --> Allows web app to access data only within scope
    params = {
        'client_id': client_id,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': REDIRECT_URI,
        'show_dialog': True     #should remove this line later: forces the user to login in everytime b/c easier to test/debug
    }

    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    print(auth_url)
    return redirect(auth_url)

@app.route('/callback')
def callback():
    #Check if there's an error in login in to Spotify account
    if 'error' in request.args:
        return jsonify({"error": request.args['error']})
    
    #Valid login to Spotify account 
    if 'code' in request.args:
        req_body = {
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URI,
            'client_id': client_id,
            'client_secret': client_secret
        }

        result = post(TOKEN_URL, data=req_body)
        json_result = result.json()

        #Retrieving data from json_result --> Put data into session for security purposes
        session['access_token'] = json_result['access_token']
        session['refresh_token'] = json_result['refresh_token']
        session['expires_at'] = datetime.now().timestamp() + json_result['expires_in']      #Converting 'expires_in' seconds into date

        #Creating variables in session --> tracks' features to update
        session['total_studysessions'] = 0
        session['total_songs'] = 0
        session['avg_acousticness'] = 0
        session['avg_duration_ms'] = 0
        session['avg_energy'] = 0
        session['avg_instrumentalness'] = 0
        session['avg_liveness'] = 0
        session['avg_loudness'] = 0
        session['avg_speechiness'] = 0
        session['avg_tempo'] = 0
        session['avg_valence'] = 0

        #Creating variables --> get_recommendations parameters user can adjust
        session['seed_artists'] = []
        session['seed_tracks'] = []
        session['seed_genres'] = []
        
        return redirect('/')