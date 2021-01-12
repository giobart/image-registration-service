import pymongo
from config import DB_ADDRESS

client = None
collection = None


def db_init():
    global client
    global collection
    if client is None:
        client = pymongo.MongoClient(DB_ADDRESS)
        collection = client.whosthatpokemon.users


def db_insert(img_dict):
    global collection
    res = collection.insert_one(img_dict)
    return res


def db_delete_by_id(id):
    global collection
    myquery = {"_id": id}
    collection.delete_one(myquery)


def get_all_batch(batch_size, page):
    global collection
    cursor = collection.find().limit(batch_size).skip((page - 1) * batch_size)
    return [x for x in cursor]
