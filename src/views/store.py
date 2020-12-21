from flask import Blueprint, request, jsonify
from src.utility.db import *

store = Blueprint('store', __name__)

'''
    /store a new user image
    input JSON format: 
        {"name":"str", "surname":"str", "employer_id":"str", "img_features":[float]} 
'''


@store.route('/api/store', methods=['POST'])
def store_image():
    req = request.json

    try:

        # getting username and password from input json
        name = req['name'].strip()
        surname = req['surname'].strip()
        employer_id = req['employer_id'].strip()
        img = req['img']
        img_dict = {"name": name, "surname": surname, "_id": employer_id, "img": img}
        db_insert(img_dict)

    except Exception as e:
        # log something here
        print(e)
        return str(e), 500

    return "ok", 200


@store.route('/api/get_all/<int:page_size>/<int:page>', methods=['GET'])
def get_image(page=0, page_size=10):
    resp = ""

    if page <=0:
        return "invalid_page",500
    if page_size <=0:
        return "invalid_page_size",500

    try:

        elems = get_all_batch(page_size, page)
        resp = jsonify({"users": elems})

    except Exception as e:
        # log something here
        print(e)
        return str(e), 500

    return resp, 200

@store.route('/api/<id>', methods=['DELETE'])
def delete_image(id):
    try:

        db_delete_by_id(id)

    except Exception as e:
        # log something here
        print(e)
        return str(e), 500

    return "ok", 200
