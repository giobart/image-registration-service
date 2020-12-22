import base64
import io
from PIL import Image


def base64_to_pil(img):
    msg = base64.b64decode(img)
    buf = io.BytesIO(msg)
    img = Image.open(buf)
    return img


def is_model_downloaded():
    pass


def model_init():
    pass


def extract_features(img):
    raise Exception("Operation not supported yet")
