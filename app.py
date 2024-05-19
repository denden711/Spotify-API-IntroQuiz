import os
import random
import string
from flask import Flask, jsonify, render_template, request
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

# 'eventlet'が正しくインストールされているか確認し、'async_mode'を指定
async_mode = 'eventlet'
socketio = SocketIO(app, async_mode=async_mode)

client_id = os.getenv('SPOTIPY_CLIENT_ID')
client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

rooms = {}

def generate_room_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@app.route('/quiz', methods=['POST'])
def get_quiz():
    playlist_id = request.form['playlist_id']
    results = sp.playlist_tracks(playlist_id)
    tracks = [
        {
            'name': item['track']['name'],
            'artist': item['track']['artists'][0]['name'],
            'preview_url': item['track']['preview_url']
        } for item in results['items'] if item['track']['preview_url']
    ]
    random_track = random.choice(tracks)
    return jsonify(random_track)

@app.route('/')
def home():
    return render_template('index.html')

@socketio.on('create_room')
def on_create_room(data):
    room_id = generate_room_id()
    rooms[room_id] = {
        'host': data['username'],
        'playlist_id': '',
        'current_track': None,
        'clients': []
    }
    emit('room_created', {'room_id': room_id})

@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    if room in rooms:
        rooms[room]['clients'].append(data['username'])
        emit('status', {'msg': f'{data["username"]} has entered the room.'}, room=room)
        emit('room_data', {'clients': rooms[room]['clients'], 'host': rooms[room]['host']}, room=room)
    else:
        emit('error', {'msg': 'Room does not exist.'})

@socketio.on('leave')
def on_leave(data):
    room = data['room']
    leave_room(room)
    if room in rooms and data['username'] in rooms[room]['clients']:
        rooms[room]['clients'].remove(data['username'])
        emit('status', {'msg': f'{data["username"]} has left the room.'}, room=room)
        emit('room_data', {'clients': rooms[room]['clients'], 'host': rooms[room]['host']}, room=room)

@socketio.on('set_playlist')
def on_set_playlist(data):
    room = data['room']
    if room in rooms:
        rooms[room]['playlist_id'] = data['playlist_id']
        emit('playlist_set', {'playlist_id': data['playlist_id']}, room=room)

@socketio.on('play_track')
def on_play_track(data):
    room = data['room']
    if room in rooms:
        playlist_id = rooms[room]['playlist_id']
        results = sp.playlist_tracks(playlist_id)
        tracks = [
            {
                'name': item['track']['name'],
                'artist': item['track']['artists'][0]['name'],
                'preview_url': item['track']['preview_url']
            } for item in results['items'] if item['track']['preview_url']
        ]
        random_track = random.choice(tracks)
        rooms[room]['current_track'] = random_track
        emit('track_info', random_track, room=room)

@socketio.on('play_intro')
def on_play_intro(data):
    room = data['room']
    if room in rooms and rooms[room]['current_track']:
        track = rooms[room]['current_track']
        emit('play_intro', track, room=room)

@socketio.on('stop_intro')
def on_stop_intro(data):
    room = data['room']
    emit('stop_intro', room=room)

if __name__ == '__main__':
    import eventlet
    eventlet.monkey_patch()
    socketio.run(app, debug=True)
