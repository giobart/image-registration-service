from src.tools.model_tools import *
from src.tools.img_tools import *
import pytest
import torch
from src.tests.base64_imgs import *


@pytest.fixture
def model_initialize():
    """init the model"""
    model_init()
    return True


def test_decoding_test(model_initialize):
    tensor1 = base64_to_tensor(base64_person_1)
    tensor2 = base64_to_tensor(base64_person_1)
    assert torch.all(torch.eq(tensor1, tensor2))


def test_same_person(model_initialize):
    tensor1 = base64_to_tensor(base64_person_1)
    tensor2 = base64_to_tensor(base64_person_1_bis)
    features1 = torch.FloatTensor(extract_features(tensor1))
    features2 = torch.FloatTensor(extract_features(tensor2))
    distance = calc_distance(features1, features2).tolist()
    print("distance:", distance[0])
    assert distance[0] < 1


def test_different_person(model_initialize):
    tensor1 = base64_to_tensor(base64_person_1)
    tensor2 = base64_to_tensor(base64_person_2)
    features1 = torch.FloatTensor(extract_features(tensor1))
    features2 = torch.FloatTensor(extract_features(tensor2))
    distance = calc_distance(features1, features2).tolist()
    print("distance:", distance[0])
    assert distance[0] >= 1
