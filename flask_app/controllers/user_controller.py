from flask_app import app
from flask import render_template, redirect, session, jsonify, request
from flask_app.models.user_model import User
from flask_app.models.terminal_model import Terminal

#-----------------------------------Display Routes--------------------------#
@app.get("/")
def index():#TODO improve display of error messages in template
    if 'user_id' in session:
        return redirect('/search')
    return render_template("index.html")

@app.get("/settings")
def settings():#TODO update conditional rendering in template
    if "user_id" not in session:
        return redirect("/")
    logged_user = User.retrieve_one(id=session['user_id'])
    terminals = None
    users = None
    if logged_user.account_level > 1:
        terminals = Terminal.retrieve_all(auth_required = 1)
        users = [user for user in User.retrieve_all() if user.account_level < logged_user.account_level]
    context = {
        "logged_user" : logged_user,
        "terminals" : terminals,
        "users" : users
    }
    return render_template("settings.html", **context)
#---------------------------------------------------------------------------#
#----------------------------Action Routes----------------------------------#
@app.post('/login')
def login():
    if not User.validate(request.form):
        return redirect('/')
    user = User.retrieve_by_email(email=request.form['email'])
    session['user_id'] = user.id
    return redirect('/search')

@app.get('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.post('/grant-access')
def grant_access():
    if 'user_id' not in session:
        return jsonify(status="error")
    logged_user = User.retrieve_one(id=session['user_id'])
    if logged_user.account_level < 2:
        return jsonify(status="error")
    user_id, password = User.create(request.form)
    return jsonify(password=password, id=user_id, email=request.form['email'])

@app.post('/change-password')
def change_password():#TODO update password in db
    return redirect('/')

@app.post('/update-access')
def update_access():
    if 'user_id' not in session:
        return jsonify(status="error")
    logged_user = User.retrieve_one(id=session['user_id'])
    if logged_user.account_level <= int(request.json.get('account_level', '1')):
        return jsonify(status="error")
    User.update(request.json)
    return jsonify(status="success")

@app.post('/remove-access')
def delete_access():
    if 'user_id' not in session:
        return jsonify(status="error")
    logged_user = User.retrieve_one(id=session['user_id'])
    user_to_remove = User.retrieve_one(id=request.json.get('id'))
    if logged_user.account_level <= user_to_remove.account_level:
        return jsonify(status="error")
    User.delete(request.json)
    return jsonify(status="success")
#--------------------------------------------------------------------------------#