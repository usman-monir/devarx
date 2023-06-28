from app import socketIO, openai, app, mail
from models import User
from flask import render_template, url_for, redirect, flash, session, request
from forms import SignupForm, LoginForm, RestRequestForm, ResetPasswordForm, HomePageForm
from flask_socketio import join_room, leave_room
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer as Serializer
from string import ascii_uppercase
from datetime import datetime
import random

rooms = {}

app.config["SECRET_KEY"] = "asupersecretkey"

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

    response = openai.ChatCompletion.create(model="gpt-3.5-turbo",messages=messages)
    try:
        answer = response['choices'][0]['message']['content'].replace('\n', '<br>')
    except:
        flash("Something went wrong!", "danger")
        return "Check your internet connection and try again :("
    return answer


# routes

@app.route("/", methods=["GET", "POST"])
def homepage():
    session.clear()
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
        session["name"] = name
        return redirect(url_for("room"))
    return render_template("homepage.html", form= form, title= "Home")

@app.route("/get", methods=["GET", "POST"])
def chatWithBot():
    mssg = request.form.get("mssg")
    return generateChatResponse(mssg)


@app.route("/room")
def room():
    room_code = session.get("room")
    name = session.get("name")
    if room_code is None or name is None or room_code not in rooms:
        return redirect(url_for("homepage"))
    return render_template("room.html", title="Room: " + room_code, current_user=session.get("name"))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    u = User()
    u.CreateSignupTable()
    if form.validate_on_submit():
        res = u.insertToSignup(form.username.data, form.email.data, form.password.data)
        if res:
            flash(res, "danger")
        else:
            return redirect(url_for("login"))
    return render_template('Signup.html', title="Signup", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        u = User()
        user = u.login(form.email.data, form.password.data)
        if user:
            session['email'] = form.email.data
            flash("Logged in successfully!", "success")
            return redirect(url_for("homepage"))
        else:
            flash("Incorrect email or password!", "danger")
            return redirect(url_for("login"))
    return render_template('login.html', title="Login", form=form)


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    form = RestRequestForm()
    if form.validate_on_submit():
        email = form.email.data
        u = User()
        exists = u.verify(email)
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
        user = User()
        update = user.updatePassword(password, email)
        if update:
            flash("Password've been changed! Please login.", 'success')
            return redirect(url_for('login'))
        else:
            flash('Password could not be changed due to some reason', 'danger')
    return render_template('change_password.html', title='Change Password', form=form)



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


@socketIO.on("send_message")
def message(message):
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
