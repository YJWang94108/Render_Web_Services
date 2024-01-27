from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route("/Test")
def index():
    return render_template("index.html")
    
@socketio.on('message')
def handle_message(msg):
    print('Message:', msg)
    socketio.emit('message', msg, broadcast=True)

@app.route("/")
def hello():
    return render_template("home.html")

## Main
app.run('0.0.0.0', debug=True)
    