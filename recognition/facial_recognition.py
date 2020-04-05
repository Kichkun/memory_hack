import face_recognition
import numpy as np


def extract_face_encoding(img_path):
    loaded_image = face_recognition.load_image_file(img_path)
    extracted_encoding = face_recognition.face_encodings(loaded_image)
    if extracted_encoding:
        return face_recognition.face_encodings(loaded_image, model='cnn')[0]
    return None


def find_most_similar_face(source_vectors, target_vector, threshold = 0.6):
    distances = face_recognition.face_distance(source_vectors, target_vector)
    if np.any(distances <= threshold):
        return np.argmin(distances)
    return None


if __name__ == '__main__':
    vector_real = extract_face_encoding('D:\coding\memory_hack\data_20000_30000\Лапин Николай Сергеевич.png')

    vector_source_1 = extract_face_encoding('D:\coding\memory_hack\data_20000_30000\Лапкин Владимир Владимирович.png')
    vector_source_2 = extract_face_encoding('D:\coding\memory_hack\data_20000_30000\Лапин Николай Сергеевич.png')
    vector_source_3 = extract_face_encoding('D:\coding\memory_hack\data_20000_30000\Лапкин Владимир Владимирович.png')

    vectors = [vector_source_2, vector_source_1, vector_source_3]

    print(find_most_similar_face(vectors, vector_real))

