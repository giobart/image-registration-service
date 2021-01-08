import cv2
from facenet_pytorch import MTCNN
import numpy as np
from PIL import Image
import math

ALPHA_SHIFT = 10
LEFT_EYE_POS = lambda w, h: (w / 3 + ALPHA_SHIFT, h / 3 + ALPHA_SHIFT)
RIGHT_EYE_POS = lambda w, h: ((2 * w / 3) - ALPHA_SHIFT, h / 3 + ALPHA_SHIFT)
NOSE_POS = lambda w, h: ((w / 2) + ALPHA_SHIFT, (3 * h / 5) + ALPHA_SHIFT)



def angle_between_2_points(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    tan = (y2 - y1) / (x2 - x1)
    return np.degrees(np.arctan(tan))

def get_rotation_matrix(p1, p2):
    angle = angle_between_2_points(p1, p2)
    x1, y1 = p1
    x2, y2 = p2
    xc = (x1 + x2) // 2
    yc = (y1 + y2) // 2
    M = cv2.getRotationMatrix2D((xc, yc), angle, 1)
    return M

def get_affine_transform_matrix(p1, p2, p3, d1, d2, d3):
    pts1 = np.float32([list(p1), list(p2), list(p3)])
    pts2 = np.float32([list(d1), list(d2), list(d3)])

    return cv2.getAffineTransform(pts1, pts2)


def get_translation_matrix(p1, w, h):
    x1, y1 = p1
    tx = (2*w / 5) - x1
    ty = (2*h / 5) - y1
    if abs(tx) > w / 3:
        # too big translation, lets avoid it
        tx = 0
        ty = 0
    return np.float32([[1, 0, tx], [0, 1, ty]])


def get_scaling_factor(p1, p2, w):
    x1, y1 = p1
    x2, y2 = p2
    d_x1 = math.sqrt(abs(x1 - x2) ** 2 + abs(y1 - y2) ** 2)
    d_final = (2 * w / 3) - w / 3
    return d_final / d_x1


def image_deep_alignment(img, transform_kind="crop"):
    # convert image to np array
    img = np.array(img)

    # cv2 image color conversion
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # initialize detector
    face_detector = MTCNN()
    face_detector.select_largest = True

    # detect landmark points
    detections, probs, landmarks = face_detector.detect(img, landmarks=True)

    transformed = img
    if detections is not None:

        x, y, x2, y2 = int(detections[0][0]), int(detections[0][1]), int(detections[0][2]), int(detections[0][3])
        print(x,y,x2,y2)
        left_eye = landmarks[0][0]
        right_eye = landmarks[0][1]
        nose = landmarks[0][4]
        h = img.shape[0]
        w = img.shape[1]

        if transform_kind == FaceAlignTransform.ROTATION:
            rotation = get_rotation_matrix(left_eye, right_eye)
            #translation = get_translation_matrix(left_eye, w, h)
            #translated = cv2.warpAffine(img, translation, img.shape[:2], flags=cv2.INTER_CUBIC)
            transformed = cv2.warpAffine(img, rotation, img.shape[:2], flags=cv2.INTER_CUBIC)
        elif transform_kind == FaceAlignTransform.AFFINE:
            matrix = get_affine_transform_matrix(
                left_eye, right_eye, nose,
                LEFT_EYE_POS(w, h), RIGHT_EYE_POS(w, h), NOSE_POS(w, h)
            )
            transformed = cv2.warpAffine(img, matrix, img.shape[:2], flags=cv2.INTER_CUBIC)
        elif transform_kind=="crop":
            y=y-int((y2-y)*1/3)
            if y<0:
                y=0
            y2=y2+int((y2-y)*1/3)
            if y2>h:
                y2=h-1
            x = x - int((x2 - x)*1 / 3)
            if x < 0:
                x = 0
            x2 = x2 + int((x2 - x)*1 / 3)
            if x2 > w:
                x2 = w-1
            return Image.fromarray(cv2.cvtColor(img[y:y2,x:x2,:], cv2.COLOR_BGR2RGB))
    transformed = cv2.cvtColor(transformed, cv2.COLOR_BGR2RGB)
    return Image.fromarray(transformed)

class FaceAlignTransform(object):
    """
    Align the face
    """

    ROTATION = "r"
    AFFINE = "a"

    def __init__(self, kind=AFFINE):
        self.transform_kind = kind

    def __call__(self, img):
        return image_deep_alignment(img, self.transform_kind)
