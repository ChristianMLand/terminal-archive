from sqlite3 import connect
from flask_app import app, bcrypt
from flask import render_template, redirect, session, jsonify, request, flash
from random import choice
from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models.user_model import User

@app.get("/")
def index():
    if 'user_id' in session:
        return redirect('/search')
    return render_template("index.html")

@app.post('/login')
def login():
    form = {**request.form}
    form['email'] += "@odysseylogistics.com"
    query = "SELECT * FROM users WHERE email = %(email)s;"
    connection = connectToMySQL("terminal_archive")
    user = connection.query_db(query, form)
    connection.connection.close()
    if user:
        user = user[0]
        if bcrypt.check_password_hash(user['password_hash'], form['password']):
            session['user_id'] = user['id']
        else:
            flash("Invalid Password")
    else:
        flash("Invalid Email")
    return redirect('/search')

@app.post('/change-password')
def change_password():
    #TODO update password in db
    return redirect('/')

@app.post('/grant-access')
def grant_access():
    data = {}
    data['emails'] = request.form.getlist('emails')
    data['acc_level'] = request.form.get('acc_level')
    pw = generate_password()
    data['pw'] = bcrypt.generate_password_hash(pw)
    query = '''
            INSERT INTO users
            (email, password_hash, account_level)
            VALUES
            (%(email)s, %(pw)s, %(acc_level)s);
            '''
    connection = connectToMySQL("terminal_archive")
    connection.query_db(query, data)
    connection.connection.close()

    #TODO send email to email with pw
    return redirect('/admin')


@app.post('/update-access')
def update_access():
    pass

@app.get('/generate-password')
def generate_password():
    characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$-"
    gen_pass = ""
    while len(gen_pass) < 8:
        gen_pass += choice(characters)
    pass_hash = bcrypt.generate_password_hash(gen_pass)
    return jsonify(password=gen_pass, hash=str(pass_hash))

@app.get('/logout')
def logout():
    session.clear()
    return redirect('/')