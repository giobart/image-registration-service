import base64
import io
from config import *
from os import path
import glob
import gdown
from model.CustomModelGroupLoss import *
from torchvision import transforms
from db.db_utility import *
from tools.model_tools import *
from tools.evaluation_tool import *
from tools.transform import *

model = None


def base64_to_tensor(img, crop_n_resize=True):
    model = model_init()
    msg = base64.b64decode(img)
    buf = io.BytesIO(msg)
    img = Image.open(buf).convert('RGB')
    if crop_n_resize:
        img = crop_and_resize(img, model.input_size)
    img.save("last_image.jpg")
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Resize((model.input_size, model.input_size))
    ])
    return transform(img)


def crop_and_resize(img, input_size):
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
    model.eval()
    _, fc7 = model(img.unsqueeze(0))

    # features = F.normalize(features)
    # it = inference_one(model, [(img, torch.zeros(1)), (img, torch.zeros(1))])
    # for x1, y1, logits in it:
    #    return logits.tolist()
    return fc7.tolist()


def find_img_correspondence_from_db(img):
    features = torch.FloatTensor(extract_features(img))
    it = 1
    batch = get_all_batch(50, it)
    while len(batch) > 0:
        img_batch = []
        for user in batch:
            img_batch.append(torch.FloatTensor(user['img'][0]))
        user_index, distance = find_closest_match(features, torch.stack(img_batch), match_treshold=0.8)
        print(distance)
        if user_index is not None:
            print("User: " + batch[user_index]["name"] + ":" + str(batch[user_index]["_id"]) + " logged in ")
            return batch[user_index]
        it += 1
        batch = get_all_batch(50, it)
    return None
