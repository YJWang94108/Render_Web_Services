from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "<h1>Fantasy Baseball</h1>Hello, World!"

if __name__ == '__main__':
    app.run()