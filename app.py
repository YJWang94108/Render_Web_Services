from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask import request, redirect, url_for

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

def log(text:str):
    print(f'>> [PYTHON]: {text}')

@socketio.on('connect')
def handle_connect():
    log('Client connected!')

@socketio.on('message')
def handle_message(msg):
    print('Message:', msg)
    emit('message', msg, broadcast=True)

@app.route("/Test")
def testing():
    return render_template("index.html")

# ======================================
# Home Page
# /
#
@app.route("/")
def index():
    return render_template("home.html")

# ======================================
# Login Page
# /login
#
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username")
    if not username:
        return render_template(
            "login.html",
            error="請輸入玩家名稱"
        )

    # Print Login Information
    log(f"[LOGIN] Player logged in: {username}")

    return redirect(url_for("index"))

## Main

#log('App run()')
#app.run('0.0.0.0', debug=True)

log('SocketIO run()')
socketio.run(app, host='0.0.0.0', debug=True)
    