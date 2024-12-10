## Studify
### Overview
This project is a web-based application designed to enhance user music experience. It allows users to log in via their Spotify account, start study sessions, and get music recommendations based on their listening habits. The application is designed primarily for personal use to facilitate a more productive music listening session.
### API: https://api.spotify.com
### Features
1. **User Authentication with Spotify**
    - Allow users to log in using their Spotify credentials.

2. **Home Page**
    - Provide a welcoming interface with links to login and start a study session.
    - Display personalized recommendations once authenticated.

3. **Manage Spotify Sessions**
    - Allow users to start and end study sessions.
    - During a session, track currently playing songs.
    - Save session data to a CSV file for later analysis or reference.

4. **Track Current Music**
    - Retrieve information on currently playing tracks.
    - Display track name, artist(s), and a link to the Spotify track.

5. **Music Recommendations**
    - Provide users with playlist recommendations based on current listening data.
    - Offer options for generating new music discovery routes
### Routes 
1. **Login Route**
   ** Route Name and Path ** : Login /login
   ** Request Type ** : GET
   ** Purpose ** : Redirects the user to Spotify's authentication page. This allows the application permision to access the user's Spotify data.
   ** Request Format ** GET parameters: None. 
   ** Response Format ** : HTTP Redirect to Spotify's authorization endpoint
   ** Example ** : Request in the form of cURL command, Associated HTTP redirect to Spotify's login page
