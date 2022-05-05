import json
from flask import jsonify
from flask_app import app
from flask_app.models.terminal_model import Terminal
from flask_app.models.ssl_model import SSL
from flask_app.models.container_model import Container
from flask_app.models.availability_model import Availability

api_types = {
    "terminals" : Terminal,
    "ssls" : SSL,
    "containers" : Container,
    "availabilities" : Availability
}
#TODO require api token
#-----------------------Public API Endpoints-----------------------------------#
@app.get('/api/<type>/<int:id>')
def get_item(type,id):
    if type not in api_types:
        return jsonify(status="error")
    return jsonify(api_types[type].retrieve_one(id=id).json)

@app.get('/api/<type>')
def get_all_items(type):
    if type not in api_types:
        return jsonify(status="error")
    return jsonify([item.json for item in api_types[type].retrieve_all()])
#------------------------------------------------------------------------------#