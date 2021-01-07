import base64
import io
from PIL import Image
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
        gdown.download(INCEPTION_BN_URL, INCEPTION_BN_PATH, quiet=False)


def model_init():
    global model

    if not is_model_downloaded():
        model_download()

    if model is None:

        #cnn_model = CNN_MODEL_GROUP.MyCNN
        cnn_model = CNN_MODEL_GROUP.BN_INCEPTION

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

        # scheduler_params = None

        num_classes = 10177
        # num_classes = 1000

        model = Siamese_Group(hparams=model_hparams,
                              cnn_model=cnn_model,
                              scheduler_params=scheduler_params,
                              nb_classes=num_classes,
                              finetune=False,
                              weights_path=None,
                              )

        model_result = model.load_from_checkpoint(checkpoint_path=IMG_MODEL_PATH)

    return model_result


def extract_features(img):
    global model
    _,features = model(img.unsqueeze(0)) #inference_group(model,None, X=img.unsqueeze(0))
    features = F.normalize(features)
    #it = inference_one(model, [(img, torch.zeros(1)), (img, torch.zeros(1))])
    #for x1, y1, logits in it:
    #    return logits.tolist()
    return features.tolist()[0]


def compare_images(img1, img2):
    features1 = torch.FloatTensor(img1)
    features2 = torch.FloatTensor(img2)
    distance = calc_distance(features1, features2)
    print(distance)
    return distance


def find_img_correspondence_from_db(img):
    features = extract_features(img)
    it = 1
    batch = get_all_batch(50, it)
    found = None
    while len(batch) > 0:
        for user in batch:
            tmp_distance = compare_images(user['img'], features)
            print(tmp_distance)
            if tmp_distance < 0.2:
                found = user
                print("User: "+user["name"]+":"+str(user["_id"])+" logged in ")
                break
        if found is not None:
            return found
        it += 1
        batch = get_all_batch(50, it)
    return found
