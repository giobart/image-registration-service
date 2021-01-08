import base64
import io
from PIL import Image, ImageOps
from src.config import *
from os import path
import glob
import gdown
from src.model.CustomModelGroupLoss import *
from torchvision import transforms
from src.tools.model_tools import inference_one
from src.db.db_utility import *
from src.tools.model_tools import *
from src.tools.evaluation_tool import *
import numpy as np
from src.tools.transform import *

model = None


def base64_to_tensor(img,crop_n_resize=True):
    model = model_init()
    msg = base64.b64decode(img)
    buf = io.BytesIO(msg)
    img = Image.open(buf).convert('RGB')
    img = crop_and_resize(img,model.input_size)
    img.save("last_image.jpg")
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Resize((model.input_size, model.input_size))
    ])
    return transform(img)

def crop_and_resize(img,input_size):
    img = image_deep_alignment(img)
    old_size = img.size  # old_size[0] is in (width, height) format
    ratio = float(input_size) / max(old_size)
    new_size = tuple([int(x * ratio) for x in old_size])
    img = img.resize(new_size, Image.ANTIALIAS)
    new_im = Image.new("RGB", (input_size, input_size))
    new_im.paste(img, ((input_size - new_size[0]) // 2,
                       (input_size - new_size[1]) // 2))
    img = new_im
    return image_deep_alignment(img, transform_kind="r")

def is_model_downloaded():
    if IMG_MODEL_PATH in glob.glob(path.join(IMG_MODEL_FOLDER, "*")):
        return True
    return False


def model_download():
    if not is_model_downloaded():
        if not os.path.exists(IMG_MODEL_FOLDER):
            os.makedirs(IMG_MODEL_FOLDER)
        gdown.download(IMG_MODEL_URL, IMG_MODEL_PATH, quiet=False)
        gdown.download(INCEPTION_BN_URL, INCEPTION_BN_PATH, quiet=False)


def model_init():
    global model

    if not is_model_downloaded():
        model_download()

    if model is None:

        # cnn_model = CNN_MODEL_GROUP.MyCNN
        cnn_model = CNN_MODEL_GROUP.BN_INCEPTION
        model_hparams = {}
        scheduler_params = {}
        if cnn_model == CNN_MODEL_GROUP.MyCNN:
            model_hparams = {
                "lr": 0.001,
                "weight_decay": 1e-5,
                "filter_channels": 4,
                "filter_size": 3,
                "dropout": 0.00,
                "n_hidden1": 4096,
                "n_hidden2": 2048,
                'temperature': 10,
                'num_labeled_points_class': 2,
            }

            scheduler_params = {
                "step_size": 5,
                "gamma": 0.5,
            }
        elif cnn_model == CNN_MODEL_GROUP.BN_INCEPTION:
            model_hparams = {
                "lr": 0.0001602403,
                "weight_decay": 8.465428e-5,
                'temperature': 12,
                'num_labeled_points_class': 2
            }

            scheduler_params = {
                "step_size": 10,
                "gamma": 0.5,
            }

        num_classes = 10177
        # num_classes = 1000

        model = Siamese_Group.load_from_checkpoint(checkpoint_path=IMG_MODEL_PATH,
                                                   hparams=model_hparams,
                                                   cnn_model=cnn_model,
                                                   scheduler_params=scheduler_params,
                                                   nb_classes=num_classes,
                                                   finetune=False,
                                                   weights_path=None
                                                   )

    return model


def extract_features(img):
    model = model_init()
    fc7,_ = model(img.unsqueeze(0))

    # features = F.normalize(features)
    # it = inference_one(model, [(img, torch.zeros(1)), (img, torch.zeros(1))])
    # for x1, y1, logits in it:
    #    return logits.tolist()
    return fc7.tolist()


def compare_images(img1, img2):
    model = model_init()
    diff = np.subtract(img1, img2)
    dist = np.sum(np.square(diff), 1)
    return dist/100


def find_img_correspondence_from_db(img):
    features = extract_features(img)
    it = 1
    batch = get_all_batch(50, it)
    found = None
    min=1
    while len(batch) > 0:
        for user in batch:
            tmp_distance = compare_images(user['img'], features)
            print(tmp_distance)
            if tmp_distance < min :
                min=tmp_distance
                found = user
        if found is not None:
            print("User: " + found["name"] + ":" + str(found["_id"]) + " logged in ")
            return found
        it += 1
        batch = get_all_batch(50, it)
    return found
