import abc

from storage.abstract import AbstractStorage


class AbstractParser(abc.ABC):
    def __init__(self, dir_to_save: str, storage_model: AbstractStorage):
        self.dir_to_save = dir_to_save
        self.storage_model = storage_model

    @abc.abstractmethod
    def parse(self):
        pass