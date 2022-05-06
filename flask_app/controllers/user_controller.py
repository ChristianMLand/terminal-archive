from flask_app import app
from flask import render_template, redirect, session, jsonify, request
from flask_app.models.user_model import User
from flask_app.models.terminal_model import Terminal

#-----------------------------------Display Routes--------------------------#
@app.get("/")
def index():
    if 'user_id' in session:
        return redirect('/search')
    return render_template("index.html")

@app.get("/settings")
def settings():
    if "user_id" not in session:
        return redirect("/")
    logged_user = User.retrieve_one(id=session['user_id'])
    context = {
        "logged_user" : logged_user,
        "terminals" : Terminal.retrieve_all(auth_required = 1),
        "users" : [user for user in User.retrieve_all() if user.account_level < logged_user.account_level]
    }
    return render_template("settings.html", **context)
#----------------------------Action Routes----------------------------------#
@app.post('/login')
def login():
    if not User.validate(request.form):
        return redirect('/')
    user = User.retrieve_one(email=request.form['email'])
    session['user_id'] = user.id
    return redirect('/search')

@app.get('/logout')
def logout():
    session.clear()
    return redirect('/')
#--------------------------------------------------------------------------------#