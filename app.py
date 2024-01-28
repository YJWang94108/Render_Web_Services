from flask import Flask, render_template
from flask_socketio import SocketIO, emit

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
def index():
    return render_template("index.html")

@app.route("/")
def hello():
    return render_template("home.html")

## Main

#log('App run()')
#app.run('0.0.0.0', debug=True)

log('SocketIO run()')
socketio.run(app, host='0.0.0.0', debug=True)
    