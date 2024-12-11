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
   - Route Name and Path : Login /login
   - Request Type  : GET
   -  Purpose  : Redirects the user to Spotify's authentication page. This allows the application permision to access the user's Spotify data.
   -  Request Format  GET parameters: None. 
   -  Response Format  : HTTP Redirect to Spotify's authorization endpoint
   -  Example  : Request in the form of cURL command, Associated HTTP redirect to Spotify's login page
2. **Index**
- Route Name and Path : `/`  
- Request Type : `GET`  
- Purpose : Displays a welcome message and provides links to key functionalities like logging in, starting a study session, and getting recommendations.  
- Response Format :  
  Returns a welcome message with links in HTML format, such as:
  - "Login with Spotify"
  - "Start Study Session"
  - "Get Recommendations"
 3. **Authorization Callback**
- Route Name and Path: `/callback`  
- Request Type: `GET`  
- Purpose : Processes Spotify's response after a user logs in. Handles error messages or successful authentication.  
- Request Format
  - Exchanges authorization code for tokens (access and refresh).
  - Saves the tokens in the session for secure access.
- Response Format
  - Redirects to `/` on successful login.
  - Returns an error message if login fails.
  4. **Refresh Access Token**
- Route Name and Path: `/refresh-token`  
- Request Type: `GET`  
- Purpose: Refreshes the Spotify access token when the current one has expired.  
- Request Format: 
  - A valid refresh token must exist in the session.
  - The current access token must have expired.
  - Requests a new access token and updates its data in the session.
- Response Format:
  - Redirects to `/` if the refresh is successful.
  - Redirects to `/login` if the refresh token is missing.
  5. **Start a Study Session**
- Route and Path: `/studysession`  
- Request Type: `GET`  
- Purpose: Initiates a "study session" and tracks the user's currently playing songs for the duration of the session. Saves the session data into a CSV file.  
  - Monitors currently playing tracks using Spotify's API.
  - Records each unique track during the session.
  - Saves the collected data to `studysessionX.csv` (where `X` is the count of study sessions) for further analysis.
- Session Storage:
  - The session tracks the `total_studysessions` value to generate the appropriate file name.
- Response Format:  
  Redirects to `/` after recording the session.
