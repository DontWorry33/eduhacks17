from flask import Flask
from flask import jsonify
from flask import request
from flask import Response
from flask import abort
from flask import session
from flask import render_template
from flask import url_for
from flask import redirect


import os

from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect, send
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


app.config['SECRET_KEY'] = "12345"
app.config['SERVER_NAME'] = "127.0.0.1:5000"


def get_room_by_name(room_name):
    current_room = my_session["rooms"]
    return current_room[room_name]

# def python(room_name):
#     print ("pyhton called")
#

@app.route('/python/<room_name>')
def python(room_name):
    print("my_session is: ",   my_session)
    print("python: "+ room_name)
    room = get_room_by_name(room_name)
    roomcpy = room.copy()
    roomcpy["solutions"] = {}
    return render_template('joinroom.html', data=roomcpy)


@app.route('/leaderboarddata/<room_name>')
def leaderboarddata(room_name):
    room = get_room_by_name(room_name)
    stats = room["analytics"]
    stats['room'] = room_name
    #print(stats);
    return jsonify(stats)

@app.route('/leaderboard/<room_name>')
def leaderboard(room_name):
    room = get_room_by_name(room_name)
    stats = room["analytics"]
    stats['room'] = room_name
    return render_template('leaderboard.html', data=stats)

@app.route('/')
def index():
    return render_template('splash.html')


# region socketio stuff
@socketio.on('my_event', namespace='/test')
def test_message(message):
    my_session['receive_count'] = my_session.get('receive_count', 0) + 1
    print("my_session: ", my_session)
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
    print(message)
    try:
        room_list = my_session["rooms"]
    except:
        my_session["rooms"] = {}
        room_list = my_session["rooms"]

    if message["room"] in room_list:
        return # room already exists!

    questions = message["questions"]
    questions_struct={}
    for x in range(len(questions)):
        questions_struct[x] = str(questions[x])
    solutions = message["solutions"]

    if len(questions) != len(solutions):
        print("length of q does not match length of s")
        return; # no solution or question???

    room_list[message["room"]] = {"name": message["room"], "users": [], "questions": questions_struct, "solutions": solutions,
                                      "title": message["title"]}
    join_room(message['room'])


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
    except KeyError:
        print("excepted")
        my_session["rooms"] = {}
        room_list = my_session["rooms"]

    # questions=["what is 2+2", "print 1-5 in a list", "print a-z as keys and their corresponding ascii values as values in a dictionary"]
    # solutions = ['','','']
    # solutions = [str(x) for x in solutions]
    # questions_struct={}
    # for x in range(len(questions)):
    #     questions_struct[x] = str(questions[x])
    # #print(questions_struct)

    # create a new room with initial parameters?
    # if message["room"] not in room_list:
    #     room_list[message["room"]] = {"name": message["room"], "users": [], "questions": questions_struct, "solutions": solutions,
    #                                   "title": "RANDOM QUESTIONS!!!"}

    # if (message["room"] not in room_list):
    #     room_list[message["room"]] = {}
    try:
        curr_room = room_list[message["room"]]
    except:
        emit('room_error')
        return

    if (message["username"] in curr_room["users"]):
        return # username already exists in the room!

    curr_room["users"].append(message["username"])
    curr_room["current_user"] = message["username"]
    print(my_session)

    emit('redirect', {'url': url_for('python', room_name=message['room'])}, room=message['room'])
    #return redirect(url_for('python', room_name=message["room"]))

    #emit('my_response',
    #     {'data': '{0} has joined room: {1} says: {2}'.format(message["username"], message["room"], curr_room["welcome"]),
    #      'count': my_session['receive_count']})


@socketio.on('leave', namespace='/test')
def leave(message):
    leave_room(message['room'])
    print("leaving room")
    my_session['receive_count'] = my_session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': my_session['receive_count']})


@socketio.on('close_room', namespace='/test')
def close(message):
    print("CLOSING ROOM")
    my_session['receive_count'] = my_session.get('receive_count', 0) + 1
    emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
                         'count': my_session['receive_count']},
         room=message['room'])
    close_room(message['room'])


@socketio.on('send_to_leaderboard', namespace='/test')
def send_to_leaderboard(message):

    room_name=message['room']

    emit('redirect', {'url': url_for('leaderboard', room_name=message['room'])})


@socketio.on('verify_answer', namespace='/test')
def verify_answer(message):

    my_session['receive_count'] = my_session.get('receive_count', 0) + 1
    room_name = message["room"]
    answer = message["answer"]
    question_index = int(message["question_index"])
    curr_room = get_room_by_name(room_name)
    curr_user = message["curr_user"]
    print(room_name)
    answer = answer.lower()
    answer = "".join(answer.split())
    curr_room["solutions"][question_index] = curr_room["solutions"][question_index].lower()
    curr_room["solutions"][question_index] = "".join("".join(curr_room["solutions"][question_index].split()))
    print(curr_room["solutions"][question_index])
    print(answer)

    if answer == curr_room["solutions"][question_index]:
        print('answer in sols')

        try:
            stats = curr_room["analytics"]
        except:
            curr_room["analytics"] = {}
            stats = curr_room["analytics"]


        try:
            user_stats = stats[curr_user]
        except:
            print('setting stats to 0');
            stats[curr_user] = 0;
            user_stats = stats[curr_user]

        stats[curr_user] = stats[curr_user]+1

        print(curr_user)
        print(stats[curr_user])
        emit('my_response',
             {'verify': True, 'index' : question_index})
        return

    print('answer not in sols')
    emit('my_response',
         {'verify': False, 'index' : question_index})



@socketio.on('my_room_event', namespace='/test')
def send_room_message(message):
    print(message)
    my_session['receive_count'] = my_session.get('receive_count', 0) + 1

    print("my_session: ", my_session)
    print("Message: ", message)

    emit('my_response',
         {'data': "({0}) {1} says: {2}".format(message["room"], message["username"], message['data']), 'count': my_session['receive_count']},
         room=message['room'])


@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    my_session['receive_count'] = my_session.get('receive_count', 0) + 1
    print("DISCONNECT")
    emit('my_response',
         {'data': 'Disconnected!', 'count': my_session['receive_count']})
    disconnect()

@socketio.on('my_ping', namespace='/test')
def ping_pong():
    emit('my_pong')
# endregion

if __name__ == '__main__':
    socketio.run(app)
