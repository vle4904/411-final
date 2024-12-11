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
        'show_dialog': True
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
        
        return redirect('/')
    
@app.route('/refresh-token')
def refresh_token():
    #Check if there is a refresh_token in session
    if 'refresh_token' not in session:
        return redirect('/login')
    
    #Check if access_token has expired
    if datetime.now().timestamp() > session['expires_at']:
        req_body = {
            'grant_type': 'refresh_token',
            'refresh_token': session['refresh_token'],
            'client_id': client_id,
            'client_secret': client_secret
        }

        result = post(TOKEN_URL, data=req_body)
        new_token_info = result.json()

        #Change old access_token/expires_at for new access_token/expires_at
        session['access_token'] = new_token_info['access_token']
        session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']

        return redirect('/')
    
#Record data in a study session --> Input data into a database
@app.route('/studysession')
#starts a study session --> argument = duration of study session in minutes
def studysession():
    end_studysession = datetime.now().timestamp() + 1 * 60      #duration = 1 minute
    studysessionList = []
    session['total_studysessions'] += 1

    while(datetime.now().timestamp() < end_studysession):
        current_track_info = get_current_track()

        #Error checking: Check if there is a track currently playing
        if current_track_info != None:
            if len(studysessionList) == 0:
                studysessionList.append(current_track_info)
            elif studysessionList[-1]['name'] != current_track_info['name']:
                studysessionList.append(current_track_info)
                print(current_track_info['name'])

        #Retrieve current track every 5 seconds
        time.sleep(5)
    
    #Saving studysessionList as .csv file for Microsoft VS's SQL Database
    df = pd.DataFrame(studysessionList)
    
    df.to_csv(f"studysession{session['total_studysessions']}.csv", index=False)

    return redirect('/')

#Helper function for retreiving current_track
def get_current_track():
    url = "https://api.spotify.com/v1/me/player/currently-playing"
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    result = get(url, headers=headers)
    #Error Catching: If no song is playing 
    if result.status_code == 204:
        return None

    json_result = result.json()     

    #Check if there is an active track playing
    #Extracting certain data from json dictionary
    track_id = json_result['item']['id']
    track_name = json_result['item']['name']
    artists = json_result['item']['artists']                            #array of Artist Objects
    artists_names = ', '.join([artist['name'] for artist in artists])    #separating artist names with a comma
    link = json_result['item']['external_urls']['spotify']

    #Using dictionary to store current track's data
    current_track_info = {
        "id": track_id,
        "name": track_name,
        "artist": artists_names,
        "link": link
    }

    return current_track_info

#Running website app
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)