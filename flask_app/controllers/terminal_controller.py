import json
import xlsxwriter
from flask_app import app
from flask import render_template, jsonify, request, redirect, session
from flask_app.config.mysqlconnection import connectToMySQL
from datetime import datetime, date
from flask_app.models.user_model import User
from flask_app.models.terminal_model import Terminal
from flask_app.models.ssl_model import SSL
from flask_app.models.container_model import Container

#TODO refactor db calls into model methods
#TODO use template inheritance to avoid duplicate html

#-------------------------Display Routes---------------------------------#
@app.get("/search")
def search():
    if 'user_id' not in session:
        return redirect('/')
    context = {
        "terminals" : Terminal.retrieve_all(),
        "ssls" : SSL.retrieve_all(),
        "containers" : Container.retrieve_all(),
        "logged_user" : User.get_user_by_id(id=session['user_id'])
    }
    return render_template("search.html", **context)

@app.get("/admin")
def admin():
    if "user_id" not in session:
        return redirect("/")
    logged_user = User.get_user_by_id(id=session['user_id'])
    if logged_user.account_level < 2:
        return redirect('/settings')
    query = "SELECT * FROM terminals WHERE auth_required = 1;"
    terminals = connectToMySQL("terminal_archive").query_db(query)

    query = f"SELECT * FROM users WHERE account_level < {logged_user.account_level};"
    users = connectToMySQL("terminal_archive").query_db(query)

    context = {
        "logged_user" : logged_user,
        "terminals" : terminals,
        "users" : users
    }
    return render_template("admin.html", **context)

#TODO combine admin and settings with conditional rendering
@app.get("/settings")
def settings():
    if "user_id" not in session:
        return redirect("/")
    logged_user = User.get_user_by_id(id=session['user_id'])
    if logged_user.account_level > 1:
        return redirect('/admin')
    return render_template("admin.html", logged_user=logged_user)
#------------------------------------------------------------------------#
#------------------------Action Routes-----------------------------------#
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
            containers.size as "container_size", 
            availabilities.type as "available_for", 
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
        query += 'AND ' + 'AND '.join(f'''{key} in ({", ".join(f"'{v}'" for v in data[key])})''' for key in data)
    query += "ORDER BY created_at DESC;"
    results = connectToMySQL("terminal_archive").query_db(query)
    write_to_worksheet(results)
    return jsonify(data=results)

@app.get('/terminals/<int:id>')
def get_terminal(id):
    query = "SELECT * FROM terminals WHERE id=%(id)s;"
    connection = connectToMySQL("terminal_archive")
    terminal = connection.query_db(query, {"id": id})
    connection.connection.close()
    return jsonify(terminal=terminal[0])

#TODO update terminals/update to use ajax w jsonify
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

#TODO provide better information in json response
@app.get("/fetch-new-data")
def fetch_new_data():
    for terminal in Terminal.retrieve_all():
        data = terminal.parse()
        terminal.update_db(data)
    return jsonify(status="success")

def write_to_worksheet(data):
    workbook = xlsxwriter.Workbook("flask_app/static/output.xlsx")
    worksheet = workbook.add_worksheet("Picks and Drops")
    border = workbook.add_format({"border" : 1, "align" : "center"})
    gray = workbook.add_format({
        "border" : 1,
        "align" : "center",
        "bg_color" : "gray",
        "font_color" : "white"
    })
    
    for i, key in enumerate(data[0]):
        worksheet.write(0, i, key, gray)
    for i, availability in enumerate(data):
        for j, key in enumerate(availability):
            value = str(availability[key])
            worksheet.write(i+1, j, value)
            worksheet.set_column(j, j, len(value) + 10, border)
    workbook.close()