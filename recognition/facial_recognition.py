import face_recognition
import numpy as np


def extract_face_encoding(img_path):
    loaded_image = face_recognition.load_image_file(img_path)
    return face_recognition.face_encodings(loaded_image)[0]


def find_similar_faces(source_vectors, target_vector):
    return face_recognition.compare_faces(source_vectors, target_vector)


if __name__ == '__main__':
    vector_real = extract_face_encoding('D:\coding\memory_hack\data_20000_30000\Aбaлихин Владимир.png')

    vector_source_1 = extract_face_encoding('D:\coding\memory_hack\data_20000_30000\Aбaлихин Владимир.png')
    vector_source_2 = extract_face_encoding('D:\coding\memory_hack\data_20000_30000\Aверьянов Вaлерьян Яковлевич.png')
    vector_source_3 = extract_face_encoding('D:\coding\memory_hack\data_20000_30000\Aбрамянц Рубен Балаевич.png')

    vectors = [vector_source_2, vector_source_1, vector_source_3]
    results = np.array(find_similar_faces(vectors, vector_real))
    matches = np.where(results == True)
