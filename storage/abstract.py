import abc
import typing as tp


class AbstractStorage(abc.ABC):
    @abc.abstractmethod
    def store_record(self, record: tp.Any, **kwargs):
        pass

    @abc.abstractmethod
    def store_records(self, records: tp.List[tp.Any]):
        pass
