from cmath import log
import json
from flask_app import app
from flask import render_template, jsonify, request, redirect, session
from flask_app.config.mysqlconnection import connectToMySQL
from datetime import datetime, date
from flask_app.models.user_model import User
from flask_app.config.parser import parse_terminal_and_update_DB

#TODO refactor db calls into model methods
#TODO use template inheritance to avoid duplicate html

@app.get("/search")
def search():
    if 'user_id' not in session:
        return redirect('/')

    connection = connectToMySQL("terminal_archive")
    query = "SELECT id, name FROM terminals;"
    terminals = connection.query_db(query)
    query = "SELECT id, name FROM ssls;"
    ssls = connection.query_db(query)
    query = "SELECT id, size FROM containers;"
    containers = connection.query_db(query)
    connection.connection.close()

    context = {
        "terminals" : terminals,
        "ssls" : ssls,
        "containers" : containers,
        "logged_user" : User.get_user_by_id(id=session['user_id'])
    }

    return render_template("search.html", **context)

@app.post("/filter")
def filter():
    form = request.form
    start_time = form.get('start_date')
    end_time = form.get('end_time')

    start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M') if start_time else date.today()
    end_time = datetime.strptime(end_time, '%Y-%m-%dT%H:%M') if end_time else datetime.now()

    query = f'''
SELECT 
terminals.name as "terminal", 
ssls.name AS "ssl", 
containers.size as "container", 
availabilities.type as "available", 
availabilities.created_at AS "available_on"
FROM availabilities
JOIN terminals ON availabilities.terminal_id = terminals.id
JOIN ssls ON availabilities.ssl_id = ssls.id
JOIN containers ON availabilities.container_id = containers.id
WHERE created_at
BETWEEN "{start_time}"
AND "{end_time}"
'''
    data = {}
    for key in form:
        data[key] = form.getlist(key)
    data.pop('start_date')
    data.pop('end_date')
    if data.get('type'):
        query += f'AND type LIKE "%{",".join(data.pop("type"))}%" '
    if data:
        query += 'AND ' + '\nAND '.join(f'''{key} in ({", ".join(f"'{v}'" for v in data[key])})''' for key in data)
    query += "\nORDER BY created_at DESC;"
    connection = connectToMySQL("terminal_archive")
    results = connection.query_db(query)
    connection.connection.close()
    return jsonify(data=results)

@app.get("/admin")
def admin():
    if "user_id" not in session:
        return redirect("/")
    logged_user = User.get_user_by_id(id=session['user_id'])
    if logged_user.account_level < 2:
        return redirect('/settings')
    connection = connectToMySQL("terminal_archive")
    query = "SELECT * FROM terminals WHERE auth_required = 1;"
    terminals = connection.query_db(query)

    query = f"SELECT * FROM users WHERE account_level < {logged_user.account_level};"
    users = connection.query_db(query)
    connection.connection.close()

    context = {
        "logged_user" : logged_user,
        "terminals" : terminals,
        "users" : users
    }
    return render_template("admin.html", **context)

@app.get('/terminals/<int:id>')
def get_terminal(id):
    query = "SELECT * FROM terminals WHERE id=%(id)s;"
    connection = connectToMySQL("terminal_archive")
    terminal = connection.query_db(query, {"id": id})
    connection.connection.close()
    return jsonify(terminal=terminal[0])

@app.get("/settings")
def settings():
    if "user_id" not in session:
        return redirect("/")
    logged_user = User.get_user_by_id(id=session['user_id'])
    if logged_user.account_level > 1:
        return redirect('/admin')
    return render_template("admin.html", logged_user=logged_user)

@app.post("/terminals/update")
def update_terminal():
    connection = connectToMySQL("terminal_archive")
    query = '''
            UPDATE terminals 
            SET auth_email=%(auth_email)s, auth_password=%(auth_password)s
            WHERE id=%(terminal_id)s;
            '''
    connection.query_db(query, request.form)
    connection.connection.close()
    return redirect('/admin')

@app.get("/fetch-new-data")
def fetch_new_data():
    query = "SELECT * FROM terminals;"
    connection = connectToMySQL("terminal_archive")
    terminals = connection.query_db(query)
    connection.connection.close()

    for terminal in terminals:
        parse_terminal_and_update_DB(terminal)
    
    return jsonify(status="success")
