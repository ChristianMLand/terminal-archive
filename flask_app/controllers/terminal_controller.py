from cmath import log
import json
from flask_app import app
from flask import render_template, jsonify, request, redirect, session
from flask_app.config.mysqlconnection import connectToMySQL
from datetime import date
from flask_app.models.user_model import User

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
    query = f'''
            SELECT 
            terminals.name as "terminal", 
            ssls.name AS "ssl", 
            containers.size as "container", 
            availabilities.type as "available", 
            availabilities.created_at AS "available_on"
            FROM availabilities
            JOIN partnerships ON partnerships.id = availabilities.partnership_id
            JOIN terminals ON partnerships.terminal_id = terminals.id
            JOIN ssls ON partnerships.ssl_id = ssls.id
            JOIN containers ON availabilities.container_id = containers.id
            WHERE DATE(created_at) 
            BETWEEN "{form.get('start_date') or date.today()}"
            AND "{form.get('end_date') or date.today()}"
            '''
    data = {}
    for key in form:
        data[key] = form.getlist(key)
    data.pop('start_date')
    data.pop('end_date')
    if data.get('type'):
        query += f'AND type LIKE "%{",".join(i for i in data.pop("type"))}%"'
    if data:
        query += ' AND ' + ' AND '.join(f'''{key} in ({", ".join(f"'{v}'" for v in data[key])})''' for key in data)
    query += ";"
    connection = connectToMySQL("terminal_archive")
    results = connection.query_db(query)
    connection.connection.close()
    return jsonify(data=results)

@app.get("/admin")
def admin():
    if "user_id" not in session:
        return redirect("/")
    logged_user = User.get_user_by_id(id=session['user_id'])
    if logged_user.account_level < 3:
        return redirect('/settings')
    connection = connectToMySQL("terminal_archive")
    query = "SELECT * FROM terminals;"
    terminals = connection.query_db(query)

    query = "SELECT * FROM users;"
    users = connection.query_db(query)
    connection.connection.close()

    context = {
        "logged_user" : logged_user,
        "terminals" : terminals,
        "users" : users
    }
    #TODO retrieve all terminals auth data to prefill forms
    #TODO retrieve users with admin level 2 to prefill whitelist form
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
    if logged_user.account_level == 3:
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