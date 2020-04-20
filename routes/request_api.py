"""The Endpoints to manage the Health record requests"""

import copy
from flask import json, jsonify, abort, request, Blueprint
from validate_email import validate_email
from bson import json_util

# import the MongoClient classes
from pymongo import MongoClient, errors

REQUEST_API = Blueprint('request_api', __name__)

# read property file for attributes
propertydict = {}
with open("static/properties.txt") as pfile:
    for line in pfile:
        key, value = line.partition("=")[::2]
        propertydict[key] = value.strip()
properties = type("Names", (object,), propertydict)
print("MongoDB URL:", properties.mongodburl)
print("MongoDB database name:", properties.mongodbname)

# instantiate MongoDb connection and database
client = MongoClient(properties.mongodburl)
db = client.get_database(properties.mongodbname)
patientrecords = db.patients

# print the version of MongoDB server if connection successful
print ("MongoDB server version:", client.server_info()["version"])

def get_blueprint():
    """Return the blueprint for the main app module"""
    return REQUEST_API

@REQUEST_API.route('/request', methods=['GET'])
def get_records():
    # Retrieve all patient records
    patients = patientrecords.find()
    PATIENT_LIST = []
    for patient in patients:
        del patient['_id'] # Object id is not JSON serializable
        PATIENT_LIST.append(patient)
    return jsonify(PATIENT_LIST)

@REQUEST_API.route('/request/<string:_id>', methods=['GET'])
def get_record_by_id(_id):
    patient = patientrecords.find_one({"id":_id})
    if not patient:
        abort(404)
    # Return with a 404 error if id does not exist
    del patient['_id'] # Object id is not JSON serializable
    foundPatient = copy.deepcopy(patient)
    return jsonify(foundPatient)

@REQUEST_API.route('/request', methods=['POST'])
def create_record():
    if not request.get_json():
        abort(400, description="Request has incorrect JSON format")
    data = request.get_json(force=True)
    if not data.get('id'):
        abort(400, description="Request does not have id")
    if not validate_email(data['mailId']):
        abort(400, description="Request email has incorrect email format")
    newPatient = copy.deepcopy(data)
    patientrecords.insert_one(newPatient)
    # HTTP 201 Created
    return jsonify({"id": data.get('id')}), 201

@REQUEST_API.route('/request/<string:_id>', methods=['PUT'])
def edit_record(_id):
    if not request.get_json():
        abort(400)
    data = request.get_json(force=True)
    if not data['id']:
        abort(400)
    if not validate_email(data['mailId']):
        abort(400)
    if not patientrecords.find_one({"id":_id}):
        abort(404)
    updatedPatient = copy.deepcopy(data)
    patientrecords.replace_one({'id':_id}, updatedPatient)
    # HTTP 201 Created
    return jsonify(updatedPatient), 201

@REQUEST_API.route('/request/<string:_id>', methods=['DELETE'])
def delete_record(_id):
    if not patientrecords.find_one({"id":_id}):
        abort(404)
    patientrecords.delete_one({'id':_id})
    return '', 204
