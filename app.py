from flask import Flask, render_template
import server

app = Flask(__name__)

@app.route("/")
def hello():
    print("[TEST2]", flush=True)
    return render_template("home.html")

if __name__ == '__main__':
    server.Start()
    print(">> Testing", flush=True)
    app.run(debug=True)
    