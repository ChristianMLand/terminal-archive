import json
from flask_app import app
from flask import render_template, jsonify, request
from flask_app.config.mysqlconnection import connectToMySQL
from datetime import date

#TODO refactor db calls into model methods

@app.get("/search")
def search():
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
        "containers" : containers
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