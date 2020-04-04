import glob
import face_recognition
from imutils.face_utils import FaceAligner
import numpy as np
import imutils
import dlib
import cv2
import random

def crop_chips(image, user_id):
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
    fa = FaceAligner(predictor, desiredFaceWidth=256)
    facerec = dlib.face_recognition_model_v1('dlib_face_recognition_resnet_model_v1.dat')

    image = imutils.resize(image, width=480)

    rects = detector(image, 1)
    if len(rects) < 1:
        #cv2.imwrite(f"foo/{mark}/{user_id}_{frame}.png", image)
        return None
    descriptors = {}
    for i, rect in enumerate(rects):
        faceAligned = fa.align(image, image, rect)
        shape = predictor(faceAligned, rect)
        #descriptors[f'{user_id}_{i}'] = facerec.compute_face_descriptor(faceAligned, shape)
        descriptors[f'{user_id}_{i}'] = get_face_embeddings_from_image(faceAligned)
        cv2.imwrite(f"./wow/faces/{user_id}_{i}.png", faceAligned)
    return descriptors

def get_face_embeddings_from_image(image, convert_to_rgb=False):
    if convert_to_rgb:
        image = image[:, :, ::-1]

    # run the face detection model to find face locations
    face_locations = face_recognition.face_locations(image)

    # run the embedding model to get face embeddings for the supplied locations
    face_encodings = face_recognition.face_encodings(image, face_locations)

    return face_encodings[0]

def calc_similarity(database_dict, image):
    known_face_encodings = list(database_dict.values())
    known_face_names = list(database_dict.keys())

    face_encoding = get_face_embeddings_from_image(image)

    # get the distances from this encoding to those of all reference images
    distances = face_recognition.face_distance(known_face_encodings, face_encoding)

    # select the closest match (smallest distance) if it's below the threshold value
    if np.any(distances <= MAX_DISTANCE):
        best_match_idx = np.argmin(distances)
        name = known_face_names[best_match_idx]
    else:
        name = None

    return name, min(distances)

if __name__ == "__main__":

    MAX_DISTANCE = 0.6
    base_dir = './wow'
    photos = glob.glob(f'{base_dir}/*.png')
    all_descriptors = {}
    for photo in photos:
        print(photo)
        image = cv2.imread(photo)
        photo_id = photo.split('/')[2].split('.')[0]
        out = crop_chips(image, photo_id)
        if out != None:
            all_descriptors = {**all_descriptors, **out}
            known_face_names = list(all_descriptors.keys())
            test_id = random.choice(known_face_names)
            image = cv2.imread(f'./wow/faces/{test_id}.png')
            name, similarity  = calc_similarity(all_descriptors, image)
            print(name, similarity, test_id)
