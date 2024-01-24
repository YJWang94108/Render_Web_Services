from flask import Flask, render_template
from server import Test

app = Flask(__name__)

@app.route("/")
def hello():
    Test()
    return render_template("home.html")

if __name__ == '__main__':
    app.run()