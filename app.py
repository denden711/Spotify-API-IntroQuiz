# app.py
import os
from flask import Flask, jsonify
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

app = Flask(__name__)

client_id = os.getenv('SPOTIPY_CLIENT_ID')
client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
playlist_id = os.getenv('SPOTIPY_PLAYLIST_ID')

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

@app.route('/quiz', methods=['GET'])
def get_quiz():
    results = sp.playlist_tracks(playlist_id)
    tracks = [{'name': item['track']['name'], 'artist': item['track']['artists'][0]['name']} for item in results['items']]
    return jsonify(tracks)

@app.route('/')
def home():
    return jsonify({'message': 'Welcome to the Intro Quiz App!'})

if __name__ == '__main__':
    app.run(debug=True)
