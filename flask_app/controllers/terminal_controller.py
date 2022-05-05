import json
import xlsxwriter
from flask_app import app
from flask import render_template, jsonify, request, redirect, session
from flask_app.models.user_model import User
from flask_app.models.terminal_model import Terminal
from flask_app.models.ssl_model import SSL
from flask_app.models.container_model import Container
from flask_app.models.availability_model import Availability

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

@app.get("/settings")#TODO update conditional rendering in template
def settings():
    if "user_id" not in session:
        return redirect("/")
    logged_user = User.get_user_by_id(id=session['user_id'])
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
#------------------------------------------------------------------------#
#TODO update terminals/update to use ajax w jsonify
@app.post("/terminals/update")
def update_terminal():
    if 'user_id' not in session:
        return redirect("/")
    logged_user = User.get_user_by_id(id=session['user_id'])
    if logged_user.account_level < 2:
        return redirect("/")
    Terminal.update(request.form)
    return redirect('/admin')

#TODO provide better information in json response
@app.get("/fetch-new-data")
def fetch_new_data():
    if "user_id" not in session:
        return jsonify(status="error")
    for terminal in Terminal.retrieve_all():
        data = terminal.parse()
        Availability.create(terminal, data)
    return jsonify(status="success")

@app.post("/filter")
def filter():
    availabilities = Availability.retrieve_all(request.form)
    write_to_worksheet(availabilities)
    return jsonify(data=[availability.json for availability in availabilities])

def write_to_worksheet(data):
    workbook = xlsxwriter.Workbook("flask_app/static/output.xlsx")
    worksheet = workbook.add_worksheet("Search Results")
    border = workbook.add_format({"border" : 1, "align" : "center"})
    gray = workbook.add_format({
        "border" : 1,
        "align" : "center",
        "bg_color" : "gray",
        "font_color" : "white"
    })
    row = {
        "Terminal" : None,
        "SSL" : None,
        "Container Size" : None,
        "Available During" : None,
        "Available For" : None
    }
    for i, key in enumerate(row):
        worksheet.write(0, i, key, gray)
    for i, availability in enumerate(data):
        row['Terminal'] = availability.terminal
        row['SSL'] = availability.ssl
        row['Container Size'] = availability.container
        row['Available During'] = availability.created_at
        row['Available For'] = availability.type
        for j, key in enumerate(row):
            value = str(row[key])
            worksheet.write(i+1, j, value)
            worksheet.set_column(j, j, len(value) + 10, border)
    workbook.close()