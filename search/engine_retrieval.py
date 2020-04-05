import typing as tp
import numpy as np
import textdistance
import os
import json

from entities import GeneralEntity
from recognition.facial_recognition import extract_face_encoding, find_most_similar_face


class EngineRetrieval:
    __sim_jaccard_threshold = 0.6
    __sim_img_distance = 0.2

    def __init__(self, data: tp.List[GeneralEntity]):
        self._data = data
        self._image_embeddings = np.array([x.facial_vector for x in self._data])
        self._preprocessed_names = [x.name.lower() for x in self._data]

    def matcher(self, entity: GeneralEntity) -> GeneralEntity:
        """ищет в базе наиболее похожий entity на основе снимка и ФИО"""
        match = self.__facial_matching(entity.photo_path)
        if not match:
            match = self.__name_matching(entity.name)
            if not match:
                return entity
        found_record = self._data[match]
        found_record.facial_vector = None

        return found_record

    def __facial_matching(self, target_img: str):
        face_embedding = extract_face_encoding(target_img)
        if face_embedding is None:
            return None
        return find_most_similar_face(self._image_embeddings, face_embedding,
                                      threshold=EngineRetrieval.__sim_img_distance)

    def __name_matching(self, name: str):
        similarities = [textdistance.jaccard.normalized_similarity(name, x) for x in self._preprocessed_names]
        max_idx = np.argmax(similarities)
        if similarities[max_idx] >= EngineRetrieval.__sim_jaccard_threshold:
            return max_idx
        return None


if __name__ == '__main__':
    data_dir = '../data_20000_30000/filtered'
    records = [x for x in os.listdir(data_dir) if x.endswith('json')]
    objects = []
    for record in records:
        with open(os.path.join(data_dir, record), "rb") as read_file:
            objects.append(GeneralEntity(**json.load(read_file)))
    engine = EngineRetrieval(data=objects)

    example_image = 'D:\\coding\\memory_hack\\data_20000_30000/Лапин Петр Иванович.png'
    entity = GeneralEntity(name='Лапин Петр', date='', source_url='', photo_path=example_image)

    print(engine.matcher(entity))
