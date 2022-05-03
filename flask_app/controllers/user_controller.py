import json
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
    if 'user_id' not in session:
        return jsonify(status="error")
    logged_user = User.get_user_by_id(id=session['user_id'])
    if logged_user.account_level < 2:
        return jsonify(status="error")
    password = generate_password()
    data = {
        "email" : request.form.get('email'),
        "hash" :  bcrypt.generate_password_hash(password)
    }
    query = '''
            INSERT INTO users
            (email, password_hash)
            VALUES
            (%(email)s, %(hash)s);
            '''
    connection = connectToMySQL("terminal_archive")
    user_id = connection.query_db(query, data)
    connection.connection.close()

    print(password)

    return jsonify(password=password, id=user_id, email=data['email'])


@app.post('/update-access')
def update_access():
    if 'user_id' not in session:
        return jsonify(status="error")
    logged_user = User.get_user_by_id(id=session['user_id'])
    if logged_user.account_level <= int(request.json.get('account_level')):
        return jsonify(status="error")
    query = '''
            UPDATE users
            SET account_level = %(account_level)s
            WHERE users.id = %(id)s;
            '''
    connection = connectToMySQL("terminal_archive")
    connection.query_db(query, request.json)
    connection.connection.close()

    return jsonify(status="success")

@app.post('/remove-access')
def delete_access():
    if 'user_id' not in session:
        return jsonify(status="error")
    logged_user = User.get_user_by_id(id=session['user_id'])
    user_to_remove = User.get_user_by_id(id=request.json.get('id'))
    if logged_user.account_level <= user_to_remove.account_level:
        return jsonify(status="error")
    query = '''
            DELETE FROM users
            WHERE id = %(id)s;
            '''
    connection = connectToMySQL("terminal_archive")
    connection.query_db(query, request.json)
    connection.connection.close()

    return jsonify(status="success")

def generate_password():
    characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$-"
    gen_pass = ""
    while len(gen_pass) < 8:
        gen_pass += choice(characters)
    return gen_pass

@app.get('/logout')
def logout():
    session.clear()
    return redirect('/')