#!/usr/bin/env python
import rethinkdb as r

from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None


def background_thread():
    """Example of how to send server generated events to clients."""
    r.connect("192.168.73.35", 28015).repl()
    cursor = r.db("foosball").table("games").filter(r.row["active"] == True).changes()
    for i, row in enumerate(cursor.run()):
        if row['new_val'] == None:
            data = ""
        else:
            output = str(row['new_val'])
            player1 = row['new_val']['player1']['name']
            player2 = row['new_val']['player2']['name']
            player1_score = row['new_val']['player1']['score']
            player2_score = row['new_val']['player2']['score']

            data = {
                'player1': player1,
                'player2': player2,
                'player1_score': player1_score,
                'player2_score': player2_score
            }

        socketio.emit('my_response', data, namespace='/test')


@app.route('/')
#This works, but use the API service @ /score
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


@socketio.on('my_room_event', namespace='/test')
def send_room_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         room=message['room'])

@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    if thread is None:
        thread = socketio.start_background_task(target=background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})

if __name__ == '__main__':
    socketio.run(app, port=5010, debug=True)
