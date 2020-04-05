import typing as tp

from entities import GeneralEntity


class EngineRetrieval:
    def __init__(self, data: tp.List[GeneralEntity]):
        self._data = data
        self._image_embeddings = None # image vectors as list

