from flask import Flask, render_template
from flask_socketio import SocketIO, send

app = Flask(__name__)


@socketio.on("message")
def sendMessage(message):
    send(message, broadcast=True)
    # send() function will emit a message vent by default


@app.route("/")
def hello():
    return render_template("home.html")

if __name__ == '__main__':
    app.run(debug=True)
    