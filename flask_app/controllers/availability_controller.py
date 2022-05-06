from flask_app import app
import json
from flask import render_template, jsonify, request, redirect, session
from flask_app.utility.utils import write_to_worksheet
from flask_app.models.user_model import User
from flask_app.models.terminal_model import Terminal
from flask_app.models.ssl_model import SSL
from flask_app.models.container_model import Container
from flask_app.models.availability_model import Availability

#-------------------------Display Routes---------------------------------#
@app.get("/search")
def search():
    if 'user_id' not in session:
        return redirect('/')
    context = {
        "terminals" : Terminal.retrieve_all(),
        "ssls" : SSL.retrieve_all(),
        "containers" : Container.retrieve_all(),
        "logged_user" : User.retrieve_one(id=session['user_id'])
    }
    return render_template("search.html", **context)
#-------------------------Action Routes------------------------------------#
@app.get("/availabilites/fetch")
def fetch_new_data():
    if "user_id" not in session:
        return jsonify(status="error")

    for terminal in Terminal.retrieve_all():
        data = terminal.parse()
        # json_data = json.dumps(data, indent=4)
        # print(terminal.name, json_data)
        Availability.create(terminal, data)
    return jsonify(status="success")

@app.post("/availabilities/filter")
def filter():
    if "user_id" not in session:
        return jsonify(data=[])
    availabilities = Availability.retrieve_all(request.form)
    write_to_worksheet(availabilities)
    return jsonify(data=[availability.json for availability in availabilities])
#----------------------------------------------------------------------------#