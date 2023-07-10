from app import socketIO, openai, app, mail
from models import Users
from flask import render_template, url_for, redirect, flash, session, request
from forms import SignupForm, LoginForm, ResetRequestForm, ResetPasswordForm, GroupForm
from flask_socketio import join_room, leave_room
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer as Serializer
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
from datetime import datetime
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

app.config["SECRET_KEY"] = config.props["SECRET_KEY"]


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
            flash("Please Login again Due to some Security Issue!", "warning")
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
            clock_skew_in_seconds=2,
        )
        print(id_info)
        session["email"] = id_info.get("email")
        session["name"] = id_info.get("name")
        usersHandler = Users()
        addedAlready =  usersHandler.verify(id_info.get("email"))
        if not addedAlready:
            res = usersHandler.insertToUsers(id_info.get("name") , id_info.get("email"), "1234")
            flash(res[0], res[1])
        id = usersHandler.getUserId(id_info.get("email"), "1234")
        session["id"] = id
        session["logged_in"] = True
        return redirect(url_for("homepage"))
    except Exception as e:
        flash("SECURITY CHECK: " + str(e), "danger")
        print("SECURITY CHECK: " + str(e), "danger")
    return redirect(url_for("login"))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    session.clear()
    form = SignupForm()
    if request.method == "POST":
        username = form.username.data
        email = form.email.data
        password = form.password.data
        confirm_password = form.confirm_password.data
        if len(password) >= 4 and password == confirm_password:
            usersHandler = Users()
            res = usersHandler.insertToUsers(username, email, password)
            id = usersHandler.getUserId(email, password)
            usersHandler.saveProfile(id,username,email,'https://st3.depositphotos.com/15648834/17930/v/600/depositphotos_179308454-stock-illustration-unknown-person-silhouette-glasses-profile.jpg')
            return redirect(url_for("login", mssg=res[0], type=res[1]))
        else:
            if len(password) < 4:
                flash("Password should be at least 4 characters ", "warning")
            elif password != confirm_password:
                flash("Password not matched to confirmation password", "warning")
    return render_template('Signup.html', title="Signup", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()
    if request.args.get("mssg"):
        flash(request.args.get("mssg"), request.args.get("type"))
    loginForm = LoginForm()
    if request.method == "POST":
            usersHandler = Users()
            userData = usersHandler.login(loginForm.email.data, loginForm.password.data)
            print("User Data:", userData)
            if userData:
                session['id'] = userData[0]
                session['name'] = userData[1]
                session['email'] = userData[2]
                session["logged_in"] = True
                return redirect(url_for('editProfile'))
            return redirect(url_for("login", mssg="Incorrect email or password!", type="danger"))
    return render_template('login.html', title="Login", form=loginForm)


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


@app.route("/get", methods=["GET", "POST"])
def chatWithBot():
    mssg = request.form.get("mssg")
    res = generateChatResponse(mssg)
    return res


@app.route("/", methods=["GET", "POST"])
def homepage():
    if session.get("email") is None or session.get("name") is None:
        return redirect(url_for("login"))
    if session.get("logged_in"):
        flash("Hello " + session.get("name"), "success")
        session.pop("logged_in")
    if request.args.get('mssg') and request.args.get('type'):
        flash(request.args.get('mssg'), request.args.get('type'))

    return render_template("homepage.html", profileData = getProfileData(), title= "Home")


@app.route("/editProfile", methods=["GET","POST"])
def editProfile():
    if session.get("email") is None or session.get("name") is None:
        return redirect(url_for("login"))
    usersHandler = Users()
    profileData = getProfileData()
    if profileData is None:
        return redirect('/')
    if request.method == "POST":
        for key in request.form:
            profileData[key] = request.form.get(key)
        res = usersHandler.updateProfile(profileData)
        return redirect(url_for("homepage", mssg=res[0], type=res[1]))
    return render_template("editProfile.html", profileData=profileData)


@app.route("/createGroup", methods=["GET","POST"])
def createGroup():
    form = GroupForm()
    if request.method == "POST":
        name = form.name.data
        description = form.description.data
        usersHandler = Users()
        res = usersHandler.createGroup(name, description)
        return redirect(url_for("room", room_id=1))
    return render_template("createGroup.html", form=form, title="Create A Group")


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
        return redirect('/')


def getProfileData():
    usersHandler = Users()
    res = usersHandler.getProfile(session.get("id"))
    if res is None:
        return res
    return {
            "id": res[0],
            "username": res[1] or '',
            "email": res[2] or '',
            "firstname": res[3] or '',
            "lastname": res[4] or '',
            "about": res[5] or '',
            "phone_number": res[6] or '',
            "address": res[7]or '',
            "education": res[8] or '',
            "institution": res[9]or '',
            "interests": res[10]or '',
            "country": res[11]or '',
            "state": res[12]or '',
            "experience": res[13] or '',
            "additional_details": res[14] or '',
            "profile_photo": res[15] or '',
            "cover_photo": res[16] or ''
    }


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


def getAllGroups():
    usersHandler = Users()
    allGroups = []
    # getting all the groups
    groups = usersHandler.getAllGroups()
    for group in groups:
       allGroups.append(group)
    return allGroups


@app.route("/friendRequest", methods=["GET","POST"])
def sendFriendRequest():
    if "id" in session:
        form = GroupForm()
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
        print("pending requests:", pendingRequests, " id: ", session.get("id"))
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
            if request.form.get("accept"):
                accept = True
        except:
            if request.form.get("reject"):
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
        usersHandler = Users()
        id = session.get("id")
        myData = usersHandler.getUserData(id)
        if request.method == "GET":
            return render_template('chat.html', room_id=0, myData=None, friendData=None, groups=getAllGroups(), connections=getAllConnections(), title="Chat")
        friend_id = int(request.form.get("id"))
        friendData = usersHandler.getUserData(friend_id)
        room_id = usersHandler.getRoomId(id,friend_id)[0]
        prevChat = usersHandler.getPrevChat(room_id)
        chat = []
        if prevChat is not None:
            for data in prevChat:
                chat.append(data)
        return render_template('chat.html', myData=myData, friendData=friendData, room_id=room_id, prevChat=chat, groups=getAllGroups(), connections=getAllConnections(), title="Room - " + str(room_id) )
    else:
        return redirect('/')


@app.route("/room", methods=["GET", "POST"])
def room():
    if "id" in session:
        room_id = request.form.get("id")
        if room_id is None:
            return redirect(url_for("homepage"))
        usersHandler = Users()
        id = session.get("id")
        session["room_id"] = room_id
        myData = usersHandler.getUserData(id)
        groupData = usersHandler.getGroupData(room_id)
        prevChat = usersHandler.getPrevGroupChat(room_id)
        chat =[]
        if prevChat is not None:
            for data in prevChat:
                chat.append(data)
        return render_template("room.html", title="Room: " + room_id, myData=myData, groupData=groupData, prevChat=chat, connections=getAllConnections(),groups=getAllGroups())
    return redirect('/')


# socket methods

@socketIO.on("connect")
def connect():
    if "id" in session:
        room_id = session.get("room_id")
        id = session.get("id")
        name = session.get("name")
        if room_id is None or id is None:
            print("Cannot connect with socketIO")
            return

        join_room(room_id)
        socketIO.emit( "joinOrLeave", {"name": name, "message": " online "}, to=room_id)
        print(f"{name} has joined the room-{room_id}")
    else:
        flash("Cannot connect cz user is not login!", "danger")

@socketIO.on("disconnect")
def disconnect():
    room_id = session.get("room_id")
    name = session.get("name")
    leave_room(room_id)

    socketIO.emit( "joinOrLeave", {"name": name, "message": " online "}, to=room_id)
    print(f"{name} has left the room-{room_id}")
    redirect('/')


@socketIO.on("join_private_room")
def join_private_room(room_id):
    join_room(room_id)


@socketIO.on("send_private_message")
def send_private_message(room_id, friend_id, message):
    usersHandler = Users()
    now = datetime.now()
    formatted_date = now.strftime("%I:%M %p | %B %d")
    usersHandler.saveMessage(room_id,int(session.get("id")),int(friend_id), message, formatted_date)
    socketIO.emit('receive_mssg', {"id":session.get("id"), "message": message, "date":formatted_date}, to=room_id)


@socketIO.on("send_group_message")
def send_group_message(message):
    usersHandler = Users()
    name = session.get("name")
    room_id = session.get("room_id")
    now = datetime.now()
    formatted_date = now.strftime("%I:%M %p | %B %d")
    res = usersHandler.saveGroupMessage(room_id, session.get("id"),name, message,formatted_date)
    content = {
        "name": name,
        "message": message,
        "date": formatted_date,
        "saved": res
    }

    socketIO.emit("show_message", content, to=room_id)
