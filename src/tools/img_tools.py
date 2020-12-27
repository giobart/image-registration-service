import base64
import io
from PIL import Image
from src.config import *
from os import path
import glob
import gdown
from src.model.CustomModel import *
from torchvision import transforms
from src.tools.model_tools import inference_one

model = None


def base64_to_tensor(img):
    msg = base64.b64decode(img)
    buf = io.BytesIO(msg)
    img = Image.open(buf).convert('RGB')
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Resize((model.input_size, model.input_size))
    ])
    return transform(img)


def is_model_downloaded():
    if IMG_MODEL_PATH in glob.glob(path.join(IMG_MODEL_FOLDER, "*")):
        return True
    return False


def model_download():
    if not is_model_downloaded():
        if not os.path.exists(IMG_MODEL_FOLDER):
            os.makedirs(IMG_MODEL_FOLDER)
        gdown.download(IMG_MODEL_URL, IMG_MODEL_PATH, quiet=False)


def model_init():
    global model

    if not is_model_downloaded():
        model_download()

    if model is None:
        model_hparams = {
            "loss_fn": ContrastiveLoss(),
            "lr": 0.001,
            "weight_decay": 1e-5,
            "filter_channels": 8,
            "filter_size": 3,
            "dropout": 0.02,
            "n_hidden1": 4096,
            "n_hidden2": 2048,
            "n_hidden3": 128,
            'loss_margin': 5,
        }
        model = Siamese(hparams=model_hparams)
        model = model.load_from_checkpoint(checkpoint_path=IMG_MODEL_PATH)

    return model


def extract_features(img):
    global model
    it = inference_one(model, [(img, torch.zeros(1)),(img, torch.zeros(1))])
    for x1, y1, logits in it:
        return logits.tolist()


