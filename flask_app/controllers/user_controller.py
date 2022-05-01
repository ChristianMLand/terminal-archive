from flask_app import app
from flask import render_template, redirect, session

@app.get("/")
def index():
    return render_template("index.html")

@app.post('/login')
def login():
    #TODO authenticate login
    #TODO store id and user level in session
    return redirect('/search')

@app.get("/admin")
def admin():
    #TODO validate user level
    #TODO retrieve current terminal auth data to prefill forms
    #TODO retrieve users with admin level 2 to prefill whitelist form
    return render_template("admin.html")