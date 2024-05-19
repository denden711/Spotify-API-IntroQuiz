import os
from flask import Flask, jsonify, render_template, request
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import random

app = Flask(__name__)

# Spotify API credentials
client_id = os.getenv('SPOTIPY_CLIENT_ID')
client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')

# Initialize Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

@app.route('/quiz', methods=['POST'])
def get_quiz():
    try:
        # Get playlist ID from the form data
        playlist_id = request.form['playlist_id']
        results = sp.playlist_tracks(playlist_id)
        tracks = [
            {
                'name': item['track']['name'],
                'artist': item['track']['artists'][0]['name'],
                'preview_url': item['track']['preview_url']
            } for item in results['items'] if item['track']['preview_url']
        ]
        if not tracks:
            return jsonify({'error': 'No playable tracks found in the playlist.'}), 400
        # Randomly select a track
        random_track = random.choice(tracks)
        return jsonify(random_track)
    except spotipy.exceptions.SpotifyException as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': 'An error occurred. Please check the playlist ID and try again.'}), 500

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
