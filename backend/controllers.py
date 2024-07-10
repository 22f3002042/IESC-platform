from flask import Flask,render_template
from flask import current_app as app #alias for current running app

@app.route("/")
def home():
    return "<h2>welecome to ICSE app </h2>"

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/signup")
def signup():
    return render_template('signup.html')