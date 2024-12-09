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