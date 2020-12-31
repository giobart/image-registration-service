from flask import Blueprint, request, jsonify
from src.db.db_utility import *
from src.tools.img_tools import *

store = Blueprint('store', __name__)

'''
    /store a new user image
    input JSON format: 
        {"name":"str", "surname":"str", "employer_id":"str", "img_features":[float]} 
'''


@store.route('/api/store/<int:employee_id>', methods=['POST'])
def store_image(employee_id):
    req = request.json

    try:

        # getting username and password from input json
        name = req['name'].strip()
        surname = req['surname'].strip()
        img=""
        if 'img_features' in req:
            img = req['img_features']
        elif 'img_base64' in req:
            base = base64_to_tensor(req['img_base64'])
            img = extract_features(base)
        else:
            raise Exception("No img found")
        img_dict = {"name": name, "surname": surname, "_id": employee_id, "img": img}
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

@store.route('/api/<int:id>', methods=['DELETE'])
def delete_image(id):
    try:

        db_delete_by_id(id)

    except Exception as e:
        # log something here
        print(e)
        return str(e), 500

    return "ok", 200

@store.route('/api/find_match',methods=['POST'])
def find_match():
    req = request.json

    try:
        # getting username and password from input json
        img = req['image_base64']
        img = base64_to_tensor(img)
        result = find_img_correspondence_from_db(img)
        if result is not None:
            return jsonify(result), 200
        else:
            return "no matches found", 406

    except Exception as e:
        # log something here
        print(e)
        return str(e), 500
