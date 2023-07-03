from app import socketIO, openai, app, mail
from models import Users
from flask import render_template, url_for, redirect, flash, session, request
from forms import SignupForm, LoginForm, ResetRequestForm, ResetPasswordForm, HomePageForm
from flask_socketio import join_room, leave_room
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer as Serializer
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
from string import ascii_uppercase
from datetime import datetime
import random
import os
import pathlib
import requests
import config

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = config.props["GOOGLE_CLIENT_ID"]
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "google_auth.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)


rooms = {}

app.config["SECRET_KEY"] = config.props["SECRET_KEY"]

# utility method to generate code for a room
def generate_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)

        if code not in rooms:
            break

    return code

# utility method to generate chatgpt response

def generateChatResponse(prompt):
    messages = []
    question = {}
    question['role'] = 'system'
    question['content'] = prompt
    messages.append(question)
    answer = ""
    try:
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo",messages=messages)
        answer = response['choices'][0]['message']['content'].replace('\n', '<br>')
        print("answer" , answer)
        return answer
    except Exception as e:
        return str(e)


# routes

@app.route("/", methods=["GET", "POST"])
def homepage():
    if session.get("email") is None or session.get("name") is None:
        return redirect(url_for("login"))
    form = HomePageForm()
    if request.method == "POST":
        name = form.name.data
        code = form.code.data
        join = request.form.get("join", False)
        create = request.form.get("create", False)
        room_to_join = code
        print(name,code,create)
        if create != False:
            code = generate_code(4)
            rooms[code] = {"members": 0, "messages":[]}
            print(rooms)
            return render_template("homepage.html", form=form, title="Home", name=name, code=code)
        elif code not in rooms:
            if len(code) != 4:
                flash("Enter a valid 4-digit code for room", "warning")
            else:
                flash("Room doesn't exists!", "danger")
            return render_template("homepage.html", form=form, title="Home", name=name, code=code )

        session["room"] = room_to_join
        return redirect(url_for("room"))
    return render_template("homepage.html", form= form, title= "Home", name=session.get("name"))


@app.route("/google_login")
def google_login():
    session.clear()
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/callback")
def callback():
    try:
        if session.get("state") != request.args.get("state"):
            return redirect(url_for("login"))

        flow.fetch_token(authorization_response=request.url)

        credentials = flow.credentials
        request_session = requests.session()
        cached_session = cachecontrol.CacheControl(request_session)
        token_request = google.auth.transport.requests.Request(session=cached_session)

        id_info = id_token.verify_oauth2_token(
            id_token=credentials._id_token,
            request=token_request,
            audience=GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=-1,
        )
        print(id_info)
        session["email"] = id_info.get("email")
        session["name"] = id_info.get("name")
        usersHandler = Users()
        res = usersHandler.insertToUsers(id_info.get("name") , id_info.get("email"), "1234")
        flash(res[0], res[1])
        id = usersHandler.getUserId(id_info.get("email"), "1234")
        session["id"] = id
        homePageForm = HomePageForm()
        return render_template("homepage.html", form=homePageForm, title="Home", name=session.get("name"))
    except Exception as e:
        flash("SECURITY CHECK: " + str(e), "danger")
    return redirect(url_for("login"))


@app.route("/get", methods=["GET", "POST"])
def chatWithBot():
    mssg = request.form.get("mssg")
    res = generateChatResponse(mssg)
    return res


@app.route("/room")
def room():
    room_code = session.get("room")
    name = session.get("name")
    if room_code is None or name is None or room_code not in rooms:
        return redirect(url_for("homepage"))
    return render_template("room.html", title="Room: " + room_code, connections=getAllConnections(), current_user=session.get("name"))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    session.clear()
    form = SignupForm()
    usersHandler = Users()
    if form.validate_on_submit():
        res = usersHandler.insertToUsers(form.username.data, form.email.data, form.password.data)
        if res:
            flash(res, "danger")
        else:
            return redirect(url_for("login"))
    return render_template('Signup.html', title="Signup", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            usersHandler = Users()
            userData = usersHandler.login(form.email.data, form.password.data)
            if userData:
                session['id'] = userData[0]
                session['name'] = userData[1]
                session['email'] = userData[2]
                flash("Logged in successfully!", "success")
                return redirect(url_for("homepage"))
            else:
                flash("Incorrect email or password!", "danger")
                return redirect(url_for("login"))
    return render_template('login.html', title="Login", form=form)


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    form = ResetRequestForm()
    if form.validate_on_submit():
        email = form.email.data
        usersHandler = Users()
        exists = usersHandler.verify(email)
        if exists:
            try:
                serializer = Serializer('app')
                token = serializer.dumps([email], salt='password-reset')
                msg = Message('Password Reset', sender='noreply@devarxyu', recipients=[email])
                msg.body = f'''Click the link below to reset your password:\n\n
                {url_for('reset_with_token', token=token, _external=True)}
                if you didn't make a request. Please ignore it.
                Mohammad Usman Monir          Yasir Arfat
                @devArx
                '''
                mail.send(msg)
                flash('Password reset link has been sent to your email', 'success')
            except Exception as e:
                flash("In case you've not received the link on your mail!", "warning")
                flash("http://127.0.0.1:5000/reset_password/" + token, "success")
                print(str(e))
        else:
            flash("Invalid email", "warning")
    return render_template('reset_request.html', title='Reset Request', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_with_token(token):
    serializer = Serializer('app')
    email = serializer.loads(token, salt='password-reset', max_age=3600)
    if email is None:
        flash('That is an invalid token or it has expired. Please try again.', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        password = form.password.data
        usersHandler = Users()
        update = usersHandler.updatePassword(password, email)
        if update:
            flash("Password've been changed! Please login.", 'success')
            return redirect(url_for('login'))
        else:
            flash('Password could not be changed due to some reason', 'danger')
    return render_template('change_password.html', title='Change Password', form=form)


@app.route("/searchResult", methods=["GET","POST"])
def getSearchResults():
    if "id" in session:
        username = str(request.args["search"])
        usersData = []
        id = session.get("id")
        usersHandler = Users()
        users = usersHandler.getUserNames()

        # getting all the users except self
        for user in users:
            if user[0] != id and (username.lower() in user[1].lower() or username.lower() in user[2].lower()):
                usersData.append(user)

        return render_template("searchUsers.html", users=usersData, connections=getAllConnectionIds(), search=username, title="Add Connections")
    else:
        flash("Something went wrong!", "warning")
        return redirect(url_for("homepage"))


def getAllConnectionIds():
    usersHandler = Users()
    id = session.get("id")
    connectionIds = []
    # getting all the friends
    connections = usersHandler.getConnections(id)
    for connection in connections:
        # check which one is not user himself and then append to the array
        if int(id) == connection[1]:
            connectionIds.append(connection[2])
        else:
            connectionIds.append(connection[1])
    return connectionIds


def getAllConnections():
    usersHandler = Users()
    id = session.get("id")
    connections = []
        # getting all the friends
    connectionsIds = usersHandler.getConnections(id)
    for connection in connectionsIds:
        # check which one is not user himself and then append to the array
        if int(id) == connection[1]:
            connections.append(usersHandler.getUserData(connection[2]))
        else:
            connections.append(usersHandler.getUserData(connection[1]))
    return connections


@app.route("/friendRequest", methods=["GET","POST"])
def sendFriendRequest():
    if "id" in session:
        form = HomePageForm()
        friend_id = int(request.args["id"])
        usersHandler = Users()
        res = usersHandler.addToPending(session.get("id"), friend_id)
        flash(res[0], res[1])
        return render_template("homepage.html", form=form, title="Home")
    else:
        flash("Something went wrong!", "warning")
        return redirect('/')


@app.route("/removeFriend",  methods=["GET","POST"])
def removeFriend():
    if "id" in session:
        friend_id = int(request.args["id"])
        search = request.args["search"]
        usersHandler = Users()
        res = usersHandler.removeConnection(session.get("id"), friend_id)
        flash(res[0], res[1])
        return redirect(url_for('getSearchResults', search=search))
    else:
        flash("Something went wrong!", "warning")
        return redirect('/')

@app.route("/notifications")
def notifications():
    if "id" in session:
        usersHandler = Users()
        pendingRequests = usersHandler.getPendingRequests(session.get("id"))
        usersData = []
        for request in pendingRequests:
            usersData.append(usersHandler.getUserData(request[0]))

        print(usersData)

        return render_template('notifications.html', users=usersData, title="Notifications")
    else:
        flash("Something went wrong!", "warning")
        return redirect('/')


@app.route("/acceptOrRejectRequest", methods=["GET","POST"])
def handleAcceptOrRejectRequest():
    if "id" in session:

        friend_id = request.form.get("id")
        accept = False
        try:
            if request.form.get("accept") == "Accept":
                accept = True
        except:
            if request.form.get("reject") == "Reject":
                accept = False

        usersHandler = Users()
        usersHandler.clearFromPending(friend_id, session.get("id"))

        if accept:
            res = usersHandler.addConnection(session.get("id"), friend_id)
            flash(res[0], res[1])

        return redirect('/')

    else:
        flash("Something went wrong!", "warning")
        return redirect('/')


@app.route('/chat', methods=["POST","GET"])
def startChat():
    if "id" in session:
        friend_id = int(request.form.get("id"))
        id = int(session.get("id"))
        print(friend_id)
        usersHandler = Users()
        myData = usersHandler.getUserData(id)
        friendData = usersHandler.getUserData(friend_id)
        room_id = usersHandler.getRoomId(id,friend_id)[0]
        prevChat = usersHandler.getPrevChat(room_id)
        chat = []
        if prevChat is not None:
            for message in prevChat:
                chat.append(message)
        return render_template('chat.html', myData=myData, friendData=friendData, room_id=room_id, prevChat=chat, connections=getAllConnections(), title="Room - " + str(room_id) )
    else:
        return redirect('/')


# socket methods

@socketIO.on("connect")
def connect():
    room_code = session.get("room")
    name = session.get("name")
    if room_code is None or name is None:
        flash("Cannot connect with socketIO", "danger")
        print("Cannot connect with socketIO")
        return
    if room_code not in rooms:
        flash("Room not found", "warning")
        print("Room not found")
        leave_room(room_code)
        return

    flash("Connected Successfully", "success")
    join_room(room_code)
    rooms[room_code]["members"]+=1
    socketIO.emit( "joinOrLeave", {"name": name, "message": " has joined the room "}, to=room_code)
    print(f"{name} has joined the room-{room_code}")


@socketIO.on("disconnect")
def disconnect():
    room_code = session.get("room")
    name = session.get("name")
    leave_room(room_code)
    if room_code in rooms:
        rooms[room_code]["members"] -= 1
        if rooms[room_code]["members"] <= 0:
            del rooms[room_code]

    flash("You are disconnected", "warning")
    socketIO.emit( "joinOrLeave", {"name": name, "message": " has left the room "}, to=room_code)
    print(f"{name} has left the room-{room_code}")
    redirect(url_for("homepage"))


@socketIO.on("join_private_room")
def join_private_room(name, room_id):
    join_room(room_id)
    socketIO.emit( "joinOrLeave", {"name": name, "message": " has joined the room "}, to=room_id)


@socketIO.on("send_private_message")
def send_private_message(room_id, friend_id, message):
    usersHandler = Users()
    now = datetime.now()
    formatted_date = now.strftime("%I:%M %p | %B %d")
    usersHandler.saveMessage(room_id,int(session.get("id")),int(friend_id), message, formatted_date)
    socketIO.emit('receive_mssg', {"id":session.get("id"), "message": message, "date":formatted_date}, to=room_id)


@socketIO.on("send_message")
def send_message(message):
    name = session.get("name")
    room_code = session.get("room")
    if room_code not in rooms:
        flash("Room not found", "warning")
        print("Room not found")
        return

    now = datetime.now()
    formatted_date = now.strftime("%I:%M %p | %B %d")

    content = {
        "name": name,
        "message": message,
        "date": formatted_date
    }

    rooms[room_code]["messages"].append(content)
    socketIO.emit("show_message", content, to=room_code)
