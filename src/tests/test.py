from src.tools.model_tools import *
from src.tools.img_tools import *
import pytest
import torch
from src.tests.base64_imgs import *

model = None

@pytest.fixture
def model_initialize():
    """init the model"""
    global model
    model = model_init()
    return True


def test_decoding_test(model_initialize):
    tensor1 = base64_to_tensor(base64_person_1)
    tensor2 = base64_to_tensor(base64_person_1)
    assert torch.all(torch.eq(tensor1, tensor2))


def test_same_person(model_initialize):
    tensor1 = base64_to_tensor(base64_person_1)
    tensor2 = base64_to_tensor(base64_person_1_bis)
    features1 = np.array(extract_features(tensor1), dtype=np.float32)
    features2 = np.array(extract_features(tensor2), dtype=np.float32)
    distance = compare_images(features1, features2)
    print("distance:", distance)
    assert distance < 6


def test_different_person(model_initialize):
    tensor1 = base64_to_tensor(base64_person_1)
    tensor2 = base64_to_tensor(base64_person_2)
    features1 = np.array(extract_features(tensor1), dtype=np.float32)
    features2 = np.array(extract_features(tensor2), dtype=np.float32)
    distance = compare_images(features1, features2)
    print("distance:", distance)
    assert distance >= 1

def test_different_person_img(model_initialize):
    global model
    img1 = base64_to_tensor(base64_person_1)
    img2 = base64_to_tensor(base64_person_2)
    emb, _ = evaluation_tool.predict_batchwise(model, batch=(torch.stack([img1,img2]),torch.stack([img1,img2])))
    features2 = torch.FloatTensor(extract_features(img1))
    print("emb: ",emb)
    print("features: ",features2)
    _, distance = get_similar_ind(1, model=model, batch=(torch.stack([img1,img2]),torch.stack([img1,img2])))
    print("distance:", distance[1,0])
    assert distance[1,0]>1

def test_same_person_img(model_initialize):
    global model
    img1 = base64_to_tensor(base64_person_1)
    img2 = base64_to_tensor(base64_person_1_bis)
    _, distance = get_similar_ind(1, model=model, batch=(torch.stack([img1,img2]),torch.stack([img1,img2])))
    print("distance:", distance[1,0])
    assert distance[1,0]<1

