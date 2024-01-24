from flask import Flask, render_template
from server import Start

app = Flask(__name__)

@app.route("/")
def hello():
    return render_template("home.html")

if __name__ == '__main__':
    #Start()
    app.run()
    