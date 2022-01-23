from flask import Flask, session, render_template, redirect, url_for
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("/home.html")

@app.route("/login")
def login():
    pass

@app.route("/about")
def about():
    return "<h1>About</h1>"

if __name__ == '__main__':
    app.run(debug=True)