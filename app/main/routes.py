from flask import session, redirect, url_for, render_template, request
from . import main
from .forms import LoginForm, CreateRoom

global_data = {}

@main.route('/', methods=['GET', 'POST'])
def index():
    """Login form to enter a room."""
    join_room = LoginForm()
    if join_room.validate_on_submit():
        print(global_data)
        session['name'] = join_room.name.data
        session['room'] = join_room.room.data
        session['question'] = global_data.get('rooms').get(session['room']).get('questions')

        return redirect(url_for('.room'))

    elif request.method == 'GET':
        join_room.name.data = session.get('name', '')
        join_room.room.data = session.get('room', '')

    return render_template('createroom.html', form=join_room)


@main.route('/create', methods=['GET', 'POST'])
def create():
    create_room = CreateRoom()
    if create_room.validate_on_submit():

        rooms = global_data.get("rooms", {})

        # if room already exists
        if rooms.get(create_room.room.data,""):
            pass

        rooms[create_room.room.data] = {'name': create_room.room.data, 'questions' : [create_room.question.data]}

        global_data['rooms'] = rooms
        print(global_data)

        return redirect(url_for(".create"))

    return render_template('create.html', form=create_room)


@main.route('/room')
def room():
    """Chat room. The user's name and room must be stored in
    the session."""
    name = session.get('name', '')
    room = session.get('room', '')
    question = session.get('question','')
    if name == '' or room == '':
        return redirect(url_for('.createroom'))
    return render_template('room.html', name=name, room=room, question=question)
