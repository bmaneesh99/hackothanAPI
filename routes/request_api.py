"""The Endpoints to manage the Health record requests"""

import uuid
from flask import jsonify, abort, request, Blueprint
from validate_email import validate_email
# import the MongoClient classes
from pymongo import MongoClient, errors

REQUEST_API = Blueprint('request_api', __name__)

propertydict = {}
with open("static/properties.txt") as pfile:
    for line in pfile:
        key, value = line.partition("=")[::2]
        propertydict[key] = value.strip()
properties = type("Names", (object,), propertydict)
print("mongodburl:", properties.mongodburl)
print("mongodbname:", properties.mongodbname)

client = MongoClient(properties.mongodburl)
db = client.get_database(properties.mongodbname)

# print the version of MongoDB server if connection successful
print ("MongoDB server version:", client.server_info()["version"])


def get_blueprint():
    """Return the blueprint for the main app module"""
    return REQUEST_API

@REQUEST_API.route('/request', methods=['GET'])
def get_records():
    PATIENT_LIST = {}
    # Retrieve all patient records
    patients = db.patients.find()
    for patient in patients:
        PATIENT_LIST[patient['id']] = {
            'fullname': patient['fullname'],
            'age': patient['age'],
            'gender': patient['gender'],
            'height': patient['height'],
            'weight': patient['weight'],
            'maritalStatus': patient['maritalStatus'],
            'allergies': patient['allergies'],
            'tobaccoUse': patient['tobaccoUse'],
            'email': patient['email']}
    return jsonify(PATIENT_LIST)

@REQUEST_API.route('/request/<string:_id>', methods=['GET'])
def get_record_by_id(_id):
    PATIENT_LIST = {}
    # Retrieve all patient records to find the one with the given key
    patients = db.patients.find()
    for patient in patients:
        PATIENT_LIST[patient['id']] = {
            'fullname': patient['fullname'],
            'age': patient['age'],
            'gender': patient['gender'],
            'height': patient['height'],
            'weight': patient['weight'],
            'maritalStatus': patient['maritalStatus'],
            'allergies': patient['allergies'],
            'tobaccoUse': patient['tobaccoUse'],
            'email': patient['email']}
    if _id in PATIENT_LIST.keys():
        return jsonify(PATIENT_LIST[_id])
    else:
        abort(404)
    # Return with a 404 error if id does not exist

@REQUEST_API.route('/request', methods=['POST'])
def create_record():
    if not request.get_json():
        abort(400)
    data = request.get_json(force=True)

    if not data.get('fullname'):
        abort(400)
    if not validate_email(data['email']):
        abort(400)
    if not data.get('age'):
        abort(400)

    # Generate a new key, insert a record against this key and return the key
    new_uuid = str(uuid.uuid4())
    db.patients.insert_one(
       {
            'id':new_uuid,
            'fullname': data.get('fullname'),
            'age': data.get('age'),
            'gender': data.get('gender'),
            'height': data.get('height'),
            'weight': data.get('weight'),
            'maritalStatus': data.get('maritalStatus'),
            'allergies': data.get('allergies'),
            'tobaccoUse': data.get('tobaccoUse'),
            'email': data['email']
        }
    )
    # HTTP 201 Created
    return jsonify({"id": new_uuid}), 201

@REQUEST_API.route('/request/<string:_id>', methods=['PUT'])
def edit_record(_id):
    PATIENT_LIST = {}
    patients = db.patients.find()
    # Search through all patient records for key, return 404 error if not found
    for patient in patients:
        PATIENT_LIST[patient['id']] = {
            'fullname': patient['fullname'],
            'age': patient['age'],
            'gender': patient['gender'],
            'height': patient['height'],
            'weight': patient['weight'],
            'maritalStatus': patient['maritalStatus'],
            'allergies': patient['allergies'],
            'tobaccoUse': patient['tobaccoUse'],
            'email': patient['email']}

    if _id not in PATIENT_LIST.keys():
        abort(404)
    if not request.get_json():
        abort(400)
    data = request.get_json(force=True)

    if not data.get('fullname'):
        abort(400)
    if not validate_email(data['email']):
        abort(400)
    if not data.get('age'):
        abort(400)

    # replace the record having the given key with the new values from request
    db.patients.replace_one(
        {'id':_id},
        {
            'id':_id,
            'fullname': data.get('fullname'),
            'age': data.get('age'),
            'gender': data.get('gender'),
            'height': data.get('height'),
            'weight': data.get('weight'),
            'maritalStatus': data.get('maritalStatus'),
            'allergies': data.get('allergies'),
            'tobaccoUse': data.get('tobaccoUse'),
            'email': data['email']
        }
    )

    return jsonify(PATIENT_LIST[_id]), 200


@REQUEST_API.route('/request/<string:_id>', methods=['DELETE'])
def delete_record(_id):
    PATIENT_LIST = {}
    patients = db.patients.find()
    for patient in patients:
        PATIENT_LIST[patient['id']] = {
            'fullname': patient['fullname'],
            'age': patient['age'],
            'gender': patient['gender'],
            'height': patient['height'],
            'weight': patient['weight'],
            'maritalStatus': patient['maritalStatus'],
            'allergies': patient['allergies'],
            'tobaccoUse': patient['tobaccoUse'],
            'email': patient['email']}

    if _id not in PATIENT_LIST.keys():
        abort(404)
    db.patients.delete_one({"id":_id})
    return '', 204
