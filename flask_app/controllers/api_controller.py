import json
from flask import jsonify, session, request
from flask_app import app
from flask_app.models.terminal_model import Terminal
from flask_app.models.ssl_model import SSL
from flask_app.models.container_model import Container
from flask_app.models.availability_model import Availability
from flask_app.models.user_model import User

api_types = {
    "terminals" : Terminal,
    "ssls" : SSL,
    "containers" : Container,
    "availabilities" : Availability,
    "users" : User
}
#-----------------------API Endpoints-----------------------------------#
@app.get('/api/<type>/<int:id>')
def get_item(type,id):
    if "user_id" not in session:
        return jsonify(status="error")
    if type not in api_types:
        return jsonify(status="error")
    results = api_types[type].retrieve_one(id=id).json
    if results == False:
        return jsonify(status="error")
    return jsonify(results)

@app.get('/api/<type>')
def get_all_items(type):
    if "user_id" not in session:
        return jsonify(status="error")
    if type not in api_types:
        return jsonify(status="error")
    results = api_types[type].retrieve_all()
    if results == False:
        return jsonify(status="error")
    return jsonify([item.json for item in results])

@app.post('/api/<type>/update')
def update_item(type):
    if "user_id" not in session:
        return jsonify(status="error")
    if type not in api_types:
        return jsonify(status="error")
    form = request.form or request.json
    result = api_types[type].update(**form)
    if result == False:
        return jsonify(status="error")
    return jsonify(status="success")

@app.post('/api/<type>/create')
def create_item(type):
    if "user_id" not in session:
        return jsonify(status="error")
    if type not in api_types:
        return jsonify(status="error")
    logged_user = User.retrieve_one(id=session['user_id'])
    if logged_user.account_level < 2:
        return jsonify(status="error")
    form = request.form or request.json
    result = api_types[type].create(**form)
    if result == False:
        return jsonify(status="error")
    return jsonify(**result)

@app.post('/api/<type>/delete')
def delete_item(type):
    if "user_id" not in session:
        return jsonify(status="error")
    if type not in api_types:
        return jsonify(status="error")
    logged_user = User.retrieve_one(id=session['user_id'])
    if logged_user.account_level < 2:
        return jsonify(status="error")
    form = request.form or request.json
    result = api_types[type].delete(**form)
    if result == False:
        return jsonify(status="error")
    return jsonify(status="success")
#------------------------------------------------------------------------------#