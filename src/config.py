from src.credentials import username, password
import os

# -*- coding: utf-8 -*-
DB_ADDRESS = "mongodb+srv://" + username + ":" + password + "@cluster0.pwgbi.mongodb.net/whosthatpokemon?retryWrites=true&w=majority"
IMG_MODEL_FOLDER = os.path.join(".", "model_checkpoint")
IMG_MODEL_PATH = os.path.join(IMG_MODEL_FOLDER, "model.ckpt")
IMG_MODEL_URL = "https://drive.google.com/uc?id=1f7uCy2bDPn2ANll138uUQNuRWmjgM6yZ"
