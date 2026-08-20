from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request, redirect, url_for, session, flash
from dotenv import load_dotenv
from supabase import create_client
import os
import games

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
socketio = SocketIO(app)
SOCKET_USERS = {}

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
        .select("id, username")
        .eq("id", user_id)
        .execute()
    )

    if not response.data:
        session.clear()
        return redirect(
            url_for("login")
        )

    user = response.data[0]

    # Check if the user is already in a game
    response = (
        supabase
        .table("game_players")
        .select(
            "game_id, games(id, room_code)"
        )
        .eq("user_id", user_id)
        .execute()
    )

    current_game = None
    if response.data:
        current_game = response.data[0]

    return render_template(
        "dashboard.html",
        username=user["username"],
        current_game=current_game
    )


# ======================================
# Create Room
# /create-game
# ======================================
@app.route("/create-game")
def create_game():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    # Check if the user is already in a game
    response = (
        supabase
        .table("game_players")
        .select("game_id")
        .eq("user_id", user_id)
        .execute()
    )

    if response.data:
        return redirect(url_for("dashboard"))

    tries = 0
    while tries < 10:
        # Generate a unique room code
        room_code = games.generate_room_code()

        response = (
            supabase
            .table("games")
            .select("id")
            .eq("room_code", room_code)
            .execute()
        )

        if not response.data:
            break

        tries += 1
    
    # Create a new game
    response = (
        supabase
        .table("games")
        .insert({
            "room_code": room_code
        })
        .execute()
    )


    game = response.data[0]


    # Add the player to the game
    supabase \
        .table("game_players") \
        .insert({
            "game_id": game["id"],
            "user_id": user_id
        }) \
        .execute()


    return redirect(
        url_for(
            "game_room",
            room_code=room_code
        )
    )

# ======================================
# Join Room
# /join-game
# ======================================
@app.route("/join-game", methods=["POST"])
def join_game():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    room_code = request.form.get(
        "room_code",
        ""
    ).strip().upper()


    if not room_code:

        return redirect(
            url_for(
                "dashboard",
                error="請輸入房間碼"
            )
        )

    try:
        response = supabase.rpc(
            "join_game",
            {
                "p_room_code": room_code,
                "p_user_id": user_id
            }
        ).execute()

        result = response.data

    except Exception as e:

        log("join_game RPC error:" + str(e))
        return redirect(
            url_for(
                "dashboard",
                error="加入房間時發生錯誤"
            )
        )

    # if RPC failed
    if not result["success"]:

        error = result["error"]
        error_messages = {
            "already_in_game":
                "你已經在其他遊戲房間",
            "game_not_found":
                "找不到這個遊戲房間",
            "game_locked":
                "這個遊戲房間已經開始，無法加入",
            "game_full":
                "這個遊戲房間已經滿了"
        }

        flash(
            error_messages.get(
                error,
                "無法加入遊戲房間"
            ),
            "error"
        )

        return redirect(
            url_for(
                "dashboard"
            )
        )

    # if RPC succeeded
    return redirect(
        url_for(
            "game_room",
            room_code=result["room_code"]
        )
    )

# ======================================
# Leave Room
# /leave-game
# ======================================
@app.route("/leave-game", methods=["POST"])
def leave_game():
    global SOCKET_USERS
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    try:
        response = supabase.rpc(
            "leave_game",
            {
                "p_user_id": user_id
            }
        ).execute()
        result = response.data
    except Exception as e:
        log("leave_game RPC error: "+ str(e))
        flash(
            "退出房間時發生錯誤",
            "error"
        )

        return redirect(
            url_for("dashboard")
        )

    if not result["success"]:
        if result["error"] == "not_in_game":
            flash(
                "你目前沒有加入任何遊戲",
                "error"
            )
        else:
            flash(
                "無法退出遊戲房間",
                "error"
            )
        return redirect(
            url_for("dashboard")
        )

    room_code = result["room_code"]

    # if the game was deleted, no need to broadcast players
    if not result["game_deleted"]:

        games.broadcast_players(socketio, supabase, room_code, SOCKET_USERS)

        socketio.emit(
            "system_message",
            {
                "message":
                    "對方已退出遊戲房間"
            },
            to=room_code
        )

    response = (
        supabase
        .table("users")
        .select("username")
        .eq("id", user_id)
        .execute()
    )

    username = response.data[0]["username"]
    if not result["game_deleted"]:
        games.broadcast_players(socketio, supabase, room_code, SOCKET_USERS)
        socketio.emit(
            "player_left",
            {
                "username": username
            },
            to=room_code
        )


    return redirect(
        url_for("dashboard")
    )

# ======================================
# Socket.IO Event: join_game_room
# ======================================
@socketio.on("join_game_room")
def handle_join_game_room(data):
    global SOCKET_USERS
    room_code = data.get("room_code")
    username = data.get("username")

    if not room_code or not username:
        return

    room_code = room_code.upper().strip()
    username = username.strip()

    join_room(room_code)

    SOCKET_USERS[request.sid] = {
        "room_code": room_code,
        "username": username
    }

    log(f"User {username} joined room: {room_code}", "SOCKET.IO")
    games.broadcast_players(socketio, supabase, room_code, SOCKET_USERS)
    emit(
        "system_message",
        {
            "message": f"{username} 已上線"
        },
        to=room_code
    )

# ======================================
# Socket.IO Event: send_message
# ======================================
@socketio.on("send_message")
def handle_send_message(data):

    room_code = data.get("room_code")
    message = data.get("message", "").strip()
    username = data.get("username")

    if not room_code or not message:
        return

    room_code = room_code.upper().strip()
    username = username.strip()
    log(f"{username}: {message}", f"Room {room_code} - CHAT")

    if not username:
        return

    emit(
        "receive_message",
        {
            "username": username,
            "message": message
        },
        to=room_code
    )

# ======================================
# Socket.IO Event: disconnect
# ======================================
@socketio.on("disconnect")
def handle_disconnect():
    global SOCKET_USERS

    sid = request.sid
    user = SOCKET_USERS.pop(
        sid,
        None
    )

    if not user:
        return
    
    log(f"User {user['username']} left from room: {user['room_code']}", "SOCKET.IO")
    socketio.emit(
        "system_message",
        {
            "message":
                f"{user['username']} 已離線"
        },
        to=user['room_code']
    )
    games.broadcast_players(socketio, supabase, user['room_code'], SOCKET_USERS)


# ======================================
# Game Room
# /game/<room_code>
# ======================================
@app.route("/game/<room_code>")
def game_room(room_code):

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]


    # Check if the room exists
    response = (
        supabase
        .table("games")
        .select("id, room_code, is_locked")
        .eq("room_code", room_code)
        .execute()
    )


    if not response.data:

        return redirect(
            url_for("dashboard")
        )


    game = response.data[0]


    # Check if the player is actually in this room
    response = (
        supabase
        .table("game_players")
        .select("user_id")
        .eq("game_id", game["id"])
        .eq("user_id", user_id)
        .execute()
    )


    if not response.data:

        return redirect(
            url_for("dashboard")
        )


    # Get the players in the room
    response = (
        supabase
        .table("game_players")
        .select(
            "user_id, users(username)"
        )
        .eq("game_id", game["id"])
        .execute()
    )
    players = response.data

    # Get the current user
    response = (
        supabase
        .table("users")
        .select("username")
        .eq("id", user_id)
        .execute()
    )
    username = response.data[0]["username"]


    return render_template(
        "game_room.html",
        room_code=game["room_code"],
        username=username,
        players=players,
        is_locked=game["is_locked"]
    )
## Main

#log('App run()')
#app.run('0.0.0.0', debug=True)

log('SocketIO run()')
socketio.run(app, host='0.0.0.0', debug=True)
    