from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request, session
from requests import post, get
from datetime import datetime, timedelta
import os
import time
import urllib.parse
import json
# from flask_cors import CORS

from models import studysession_model

'''
Notes:
    Functions: 
        Start Study Sessions
        Record playing songs in a Study Session (including song data = {id, name, artist, link})
        Add/Remove Study Sessions in SQLite DB
    Common Variables:
        studysession_list: List of dictionaries (where dictionaries = played songs in a study session)
        studysession_json: JSON string of studysession_list
        study_session_id: int
'''

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
# This bypasses standard security stuff we'll talk about later
# If you get errors that use words like cross origin or flight,
# uncomment this
# CORS(app)

#Setting up variables for Spotify API
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = 'http://localhost:5000/callback'
AUTH_URL = 'https://accounts.spotify.com/authorize'
API_BASE_URL = 'https://api.spotify.com/v1/'
TOKEN_URL = "https://accounts.spotify.com/api/token"

####################################################
#
# Healthchecks
#
####################################################

@app.route('/api/health', methods=['GET'])
def healthcheck():
    """
    Health check route to verify the service is running.

    Returns:
        JSON response indicating the health status of the service
    """
    app.logger.info('Health check')
    return make_response(jsonify({'status': 'healthy'}), 200)

@app.route('/api/db-check', methods=['GET'])
def db_check() -> Response:
    """
    Route to check if the database connection and studysessions table are functional.

    Returns:
        JSON response indicating the database health status.
    Raises:
        404 error if there is an issue with the database.
    """
    try:
        app.logger.info("Checking database connection...")
        check_database_connection()
        app.logger.info("Database connection is OK.")
        app.logger.info("Checking if studysessions table exists...")
        check_table_exists("studysessions")
        app.logger.info("studysessions table exists.")
        return make_response(jsonify({'database_status': 'healthy'}), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 404)

####################################################
#
# Authentication
#
####################################################

@app.route('/login', methods=['GET'])
def login():
    """
    Login endpoint to redirect to Spotify's authorization page.

    Returns:
        JSON response with the Spotify authorization URL
    """
    scope = 'user-read-private user-read-email user-read-currently-playing'
    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': REDIRECT_URI
    }

    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    app.logger.info("Providing Spotify login URL")
    return make_response(jsonify({'auth_url': auth_url}), 200)

@app.route('/callback', methods=['GET'])
def callback():
    """
    Callback route for Spotify API.

    Returns:
        JSON response indicating success or error of token exchange
    """
    #Checks if there's an error in login in to Spotify account
    if 'error' in request.args:
        return make_response(jsonify({'error': request.args['error']}), 400)

    code = request.args.get('code')
    req_body = {
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }

    result = post(TOKEN_URL, data=req_body)
    json_result = result.json()

    #Modification --> Consider storing tokens in database as "userid"
    session['access_token'] = json_result['access_token']
    session['refresh_token'] = json_result['refresh_token']
    session['expires_at'] = datetime.now().timestamp() + json_result['expires_in']

    app.logger.info("User authenticated and tokens stored in session")
    return make_response(jsonify({'status': 'User Authenticated Successfully'}), 200)

@app.route('/refresh-token', methods=['GET'])
def refresh_token():
    """
    Refresh the Spotify access token when it expires.

    Returns:
        JSON response indicating success or error of refreshing tokens
    """
    if 'refresh_token' not in session:
        return make_response(jsonify({'error': 'No refresh token found'}), 400)

    if datetime.now().timestamp() > session['expires_at']:
        req_body = {
            'grant_type': 'refresh_token',
            'refresh_token': session['refresh_token'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }

        result = post(TOKEN_URL, data=req_body)
        new_token_info = result.json()

        #Modification: Considering storing tokens in database
        session['access_token'] = new_token_info['access_token']
        session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']

        app.logger.info("Access token refreshed")
        return make_response(jsonify({'status': 'Tokens are refreshed successfully'}), 200)

    return make_response(jsonify({'status': 'Tokens are not staled (does not need refresh)'}), 200)
    
    ##########################################################
#
# Study Sessions
#
##########################################################

@app.route('/studysession', methods=['GET'])
def studysession():
    """
    Start a study session and record currently playing tracks.

    Returns:
        JSON response indicating success or error of starting a study session

    Raises:
        400 error for unexpected errors in conducting a study session 
    """
    try:
        #studysession lasts for 5 minutes
        end_studysession = datetime.now().timestamp() + 5 * 60
        studysession_list = []

        while datetime.now().timestamp() < end_studysession:
            current_track_info = get_current_track()

            if current_track_info:
                if not studysession_list or studysession_list[-1]['name'] != current_track_info['name']:
                    studysession_list.append(current_track_info)

            time.sleep(5)

        # Convert studysession_list into JSON string
        studysession_json = json.dumps(studysession_list)

        # Store the JSON string in the database
        study_session_id = studysession_model.create_study_session(studysession_json)

        app.logger.info("Study session recorded")
        return make_response(jsonify({'status': 'Study session successfully conducted', 'study_session_id': study_session_id}), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 400)

@app.route('/api/add-study-session', methods=['POST'])
def add_study_session() -> Response:
    """
    Route to add a JSON string study session into the SQLite database.

    Expected JSON Input:
        - studysession_list (list): Study session list of dictionaries (where the dictionaries = recorded songs of a study session).

    Returns:
        JSON response indicating the success of the addition.
    Raises:
        400 error if input validation fails.
        500 error if there is an issue adding the data to the database.
    """
    app.logger.info('Adding study session to database')
    try:
        data = request.get_json()
        studysession_list = data.get('studysession_list')

        # Validate the session data
        if not isinstance(studysession_list, list):
            return make_response(jsonify({'error': 'Invalid input, session_data must be a list of dictionaries'}), 400)

        # Convert the session data to JSON string
        studysession_json = json.dumps(studysession_list)

        # Store the JSON string in the database
        study_session_id = studysession_model.create_study_session(studysession_json)

        app.logger.info('Study session data successfully added to the database')
        return make_response(jsonify({'status': 'study session data added successfully', 'study_session_id': study_session_id}), 201)

    except Exception as e:
        app.logger.error("Failed to add study session data: %s", str(e))
        return make_response(jsonify({'error': str(e)}), 500)
    
@app.route('/api/clear-study-sessions', methods=['DELETE'])
def clear_catalog() -> Response:
    """
    Route to clear all study sessions (recreate the table).

    Returns:
        JSON response indicating success or error of clearing all study sessions.
    """
    try:
        app.logger.info("Clearing all study sessions")
        studysession_model.clear_study_sessions()
        return make_response(jsonify({'status': 'success'}), 200)
    except Exception as e:
        app.logger.error(f"Error clearing study sessions: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/delete-study-session/<int:session_id>', methods=['DELETE'])
def delete_study_session(study_session_id: int) -> Response:
    """
    Route to delete a study session by its ID in the database. This performs a soft delete by marking it as deleted.

    Path Parameter:
        - study_session_id (int): The ID of the study session to delete.

    Returns:
        JSON response indicating success or error in deleting study session.
    """
    try:
        app.logger.info(f"Deleting study session by ID: {study_session_id}")

        studysession_model.delete_study_session(study_session_id)
        return make_response(jsonify({'status': 'study session deleted successfully'}), 200)
    except Exception as e:
        app.logger.error(f"Error deleting study session: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/get-study-session-by-id/<int:study_session_id>', methods=['GET'])
def get_study_session_by_id(study_session_id: int) -> Response:
    """
    Route to get a study session by its ID in the database.

    Path Parameter:
        - study_session_id (int): The ID of the study session.

    Returns:
        JSON response indicating success or error in getting study session.
    """
    try:
        app.logger.info(f"Retrieving study session by ID: {study_session_id}")

        studysession = studysession_model.get_study_session_by_id(study_session_id)
        return make_response(jsonify({'status': 'success', 'meal': studysession}), 200)
    except Exception as e:
        app.logger.error(f"Error retrieving study session by ID: {e}")
        return make_response(jsonify({'error': str(e)}), 500)
##########################################################
#
# Helper Functions
#
##########################################################

def get_current_track():
    """
    Retrieve the currently playing track from Spotify.

    Returns:
        Dictionary with track information or None if no track is playing.
    """
    url = f"{API_BASE_URL}me/player/currently-playing"
    headers = {'Authorization': f"Bearer {session.get('access_token')}"}

    result = get(url, headers=headers)
    if result.status_code == 204:
        return None

    json_result = result.json()
    track_id = json_result['item']['id']
    track_name = json_result['item']['name']
    artists = json_result['item']['artists']
    artist_names = ', '.join(artist['name'] for artist in artists)
    link = json_result['item']['external_urls']['spotify']

    return {
        'id': track_id,
        'name': track_name,
        'artist': artist_names,
        'link': link
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)