from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask import request, redirect, url_for, session
from dotenv import load_dotenv
from supabase import create_client
import os

# ========================================
# Load Environment Variables
# ========================================
load_dotenv()

# ========================================
# Flask
# ========================================

app = Flask(__name__)
# Secret Key
app.secret_key = os.getenv("SECRET_KEY")
socketio = SocketIO(app, cors_allowed_origins="*")

# ========================================
# Supabase
# ========================================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# ========================================
# Testing
# ========================================
def log(text:str, header:str="PYTHON"):
    print(f'>> [{header}]: {text}', flush=True)

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
# ======================================
@app.route("/")
def index():

    if "username" in session:
        return redirect(url_for("dashboard"))
    
    return render_template("home.html")

# ======================================
# Login Page
# /login
# ======================================
@app.route("/login", methods=["GET", "POST"])
def login():

    if "user_id" in session:
        return redirect(url_for("dashboard"))
    
    if request.method == "GET":
        return render_template("login.html")

    # Get the player's username
    username = request.form.get("username", "").strip()
    if not username:
        return render_template(
            "login.html",
            error="請輸入玩家名稱"
        )

    if len(username) > 20:
        return render_template(
            "login.html",
            error="玩家名稱最多 20 個字"
        )

    # Check if the username already exists in the database
    response = (
        supabase
        .table("users")
        .select("id, username")
        .eq("username", username)
        .execute()
    )

    if response.data:
        user = response.data[0]
        # Print Login Information
        log(f"Player logged in: {username}", "LOGIN")

    else:

        # Check the number of users
        check_num_of_users = (
            supabase
            .table("users")
            .select("id", count="exact")
            .execute()
        )

        user_count = check_num_of_users.count
        # limit
        if user_count >= 5:
            return render_template(
                "login.html",
                error="目前玩家人數已達上限，暫時無法建立新玩家"
            )

        # Create a new user
        response = (
            supabase
            .table("users")
            .insert({
                "username": username
            })
            .execute()
        )
        user = response.data[0]
        # Print Registration Information
        log(f"Player registered: {username}", "REGISTRATION")


    # Store the user's ID and username in the session
    session["user_id"] = user["id"]

    return redirect(url_for("dashboard"))

# ======================================
# Logout Page
# /logout
# ======================================
@app.route("/logout")
def logout():

    user_id = session.get("user_id")

    # Get the username for logging purposes
    response = (
        supabase
        .table("users")
        .select("username")
        .eq("id", user_id)
        .execute()
    )

    if response.data:
        username = response.data[0]["username"]
    else:
        username = "Unknown"

    log(f"Player logged out: {username}", "LOGOUT")

    # 清除 Session
    session.clear()

    return redirect(url_for("login"))

# ======================================
# Dashboard
# /dashboard
# ======================================
@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    # Check User from Supabase
    response = (
        supabase
        .table("users")
        .select("username")
        .eq("id", user_id)
        .execute()
    )

    if not response.data:
        session.clear()
        return redirect(
            url_for("login")
        )

    user = response.data[0]

    return render_template(
        "dashboard.html",
        username=user["username"]
    )

## Main

#log('App run()')
#app.run('0.0.0.0', debug=True)

log('SocketIO run()')
socketio.run(app, host='0.0.0.0', debug=True)
    