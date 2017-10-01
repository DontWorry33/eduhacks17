from flask import Flask
from flask import jsonify
from flask import request
from flask import Response
from flask import abort
from flask import session
from flask import render_template
from flask import url_for

import os

from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
from flask_cors import CORS


# instantiate the flask application
app = Flask(__name__)
socketio = SocketIO(app)
CORS(app)


#app.config.from_object('settings')


SECRET_KEY = os.environ.get("SECRET_KEY")
if SECRET_KEY == None:
    print("using flask config for secret key")
    SECRET_KEY = app.config.get('SECRET_KEY')


app.config['SECRET_KEY'] = SECRET_KEY


@app.route('/python/<room>')
def python(room):
    print("python: ", room)
    return render_template('skulpt.html', data=room)


@app.route('/')
def index():
    return render_template('index.html')


# region socketio stuff
@socketio.on('my_event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    print("Session: ", session)
    print("Message: ", message)
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})


@socketio.on('my_broadcast_event', namespace='/test')
def test_broadcast_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         broadcast=True)


@socketio.on('create', namespace='/test')
def create_room(message):
    join_room(message)

@socketio.on('join', namespace='/test')
def join(message):
    print (message)
    join_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1

    try:
        room_list = session["rooms"]
    except:
        session["rooms"] = {}
        room_list = session["rooms"]

    # create a new room with initial parameters?
    if message["room"] not in room_list:
        room_list[message["room"]] = {"users" : [], "solution": "[1,2,3,4,5]", "welcome": "welcome to excerise 1! Your output should be the following: [1,2,3,4,5]"}


    # if (message["room"] not in room_list):
    #     room_list[message["room"]] = {}

    curr_room =  room_list[message["room"]]
    if (message["username"] in curr_room["users"]) :

        return; # username already exists in the room!

    curr_room["users"].append(message["username"])


    print(session)

    emit('redirect', {'url': url_for('python', room=curr_room)})

    #emit('my_response',
    #     {'data': '{0} has joined room: {1} says: {2}'.format(message["username"], message["room"], curr_room["welcome"]),
    #      'count': session['receive_count']})


@socketio.on('leave', namespace='/test')
def leave(message):
    leave_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})


@socketio.on('close_room', namespace='/test')
def close(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
                         'count': session['receive_count']},
         room=message['room'])
    close_room(message['room'])


@socketio.on('my_room_event', namespace='/test')
def send_room_message(message):
    print(message)
    session['receive_count'] = session.get('receive_count', 0) + 1

    print("Session: ", session)
    print("Message: ", message)

    emit('my_response',
         {'data': "({0}) {1} says: {2}".format(message["room"], message["username"], message['data']), 'count': session['receive_count']},
         room=message['room'])


@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()

@socketio.on('my_ping', namespace='/test')
def ping_pong():
    emit('my_pong')
# endregion

if __name__ == '__main__':

    socketio.run(app)
