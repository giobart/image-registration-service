from credentials import username, password
import os

# -*- coding: utf-8 -*-
DB_PROTOCOL = os.getenv('MONGO_DB_PROTOCOL', "mongodb+srv")
DB_URL = os.getenv('MONGO_DB_URL', 'cluster0.pwgbi.mongodb.net/whosthatpokemon')
DB_ADDRESS = DB_PROTOCOL+"://" + username + ":" + password + "@" + DB_URL + "?retryWrites=true&w=majority"
IMG_MODEL_FOLDER = os.path.join(".", "data", "net")
IMG_MODEL_PATH = os.path.join(IMG_MODEL_FOLDER, "model.ckpt")
IMG_MODEL_URL = "https://drive.google.com/uc?id=1RXTbnrlwEhb5G0F6TfXZCVG3GC19BT-l"
INCEPTION_BN_URL = "https://drive.google.com/uc?id=1iSizx_u8lId4v92yFJVmCyxMLZdvlxTe"
INCEPTION_BN_PATH = os.path.join(IMG_MODEL_FOLDER, "bn_inception_weights_pt04.pt")
