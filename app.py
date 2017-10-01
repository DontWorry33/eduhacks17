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
my_session = {}

#app.config.from_object('settings')



SECRET_KEY = os.environ.get("SECRET_KEY")
if SECRET_KEY == None:
    print("using flask config for secret key")
    SECRET_KEY = app.config.get('SECRET_KEY')


app.config['SECRET_KEY'] = SECRET_KEY


def get_room_by_name(room_name):
    rooms = my_session["rooms"]
    return rooms[room_name]

@app.route('/python/<room_name>')
def python(room_name):
    print("python: ", room_name)
    return render_template('skulpt.html', data=get_room_by_name(room_name))


@app.route('/')
def index():
    return render_template('index.html')


# region socketio stuff
@socketio.on('my_event', namespace='/test')
def test_message(message):
    my_session['receive_count'] = my_session.get('receive_count', 0) + 1
    print("Session: ", my_session)
    print("Message: ", message)
    emit('my_response',
         {'data': message['data'], 'count': my_session['receive_count']})


@socketio.on('my_broadcast_event', namespace='/test')
def test_broadcast_message(message):
    my_session['receive_count'] = my_session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': my_session['receive_count']},
         broadcast=True)


@socketio.on('create_room', namespace='/test')
def create_room(message):

    try:
        room_list = my_session["rooms"]
    except:
        my_session["rooms"] = {}
        room_list = my_session["rooms"]

    if message["room"] in room_list:
        return # room already exists!

    questions = message["questions"]
    solutions = message["solutions"]

    if len(questions) != len(solutions):
        print("length of q does not match length of s")
        return; # no solution or question???

    room_list[message["room"]] = {"users": [], "questions": {0}, "solutions": {1}, "title": "{2}".format(questions, solutions, message["title"])}
    join_room(message)


def sol():
    ans = []
    for x in range(1,100):
        if x%2==1:
            ans.append(x)

    return ans

def sol2():
    ans = {}
    for x in range(ord('a'), ord('z')+1):
        ans[chr(x)] = x
    return ans

@socketio.on('join', namespace='/test')
def join(message):
    print (message)
    join_room(message['room'])
    my_session['receive_count'] = my_session.get('receive_count', 0) + 1

    try:
        room_list = my_session["rooms"]
    except:
        my_session["rooms"] = {}
        room_list = my_session["rooms"]

    questions=["what is 2+2", "print 1-5 in a list", "print a-z as keys and their corresponding ascii values as values in a dictionary"]
    solutions = [4, [1, 2, 3, 4, 5], sol2()]
    questions_struct={}
    solutions_struct={}
    for x in range(len(questions)):
        questions_struct[x] = str(questions[x])
        solutions_struct[x] = str(solutions[x])
    #print(questions_struct)

    # create a new room with initial parameters?
    if message["room"] not in room_list:
        room_list[message["room"]] = {"users": [], "questions": questions_struct, "solutions": solutions_struct,
                                      "title": "RANDOM QUESTIONS!!!"}

    # if (message["room"] not in room_list):
    #     room_list[message["room"]] = {}

    curr_room =  room_list[message["room"]]
    if (message["username"] in curr_room["users"]) :

        return; # username already exists in the room!

    curr_room["users"].append(message["username"])

    print(my_session)

    emit('redirect', {'url': url_for('python', room_name=message["room"])})

    #emit('my_response',
    #     {'data': '{0} has joined room: {1} says: {2}'.format(message["username"], message["room"], curr_room["welcome"]),
    #      'count': my_session['receive_count']})


@socketio.on('leave', namespace='/test')
def leave(message):
    leave_room(message['room'])
    my_session['receive_count'] = my_session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': my_session['receive_count']})


@socketio.on('close_room', namespace='/test')
def close(message):
    my_session['receive_count'] = my_session.get('receive_count', 0) + 1
    emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
                         'count': my_session['receive_count']},
         room=message['room'])
    close_room(message['room'])


@socketio.on('my_room_event', namespace='/test')
def send_room_message(message):
    print(message)
    my_session['receive_count'] = my_session.get('receive_count', 0) + 1

    print("Session: ", my_session)
    print("Message: ", message)

    emit('my_response',
         {'data': "({0}) {1} says: {2}".format(message["room"], message["username"], message['data']), 'count': my_session['receive_count']},
         room=message['room'])


@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    my_session['receive_count'] = my_session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': my_session['receive_count']})
    disconnect()

@socketio.on('my_ping', namespace='/test')
def ping_pong():
    emit('my_pong')
# endregion

if __name__ == '__main__':
    socketio.run(app)
