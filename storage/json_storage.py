import typing as tp
import json
import os
import requests

from storage.abstract import AbstractStorage


def save_img_from_url(url, path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(path, 'wb') as f:
            f.write(response.content)


class JsonStorage(AbstractStorage):
    def __init__(self, dir_to_save_in: str):
        self.dir_to_save_in = dir_to_save_in

    def store_record(self, record: tp.Dict[tp.Any, tp.Any], file_name: str):
        with open(os.path.join(self.dir_to_save_in, file_name), 'w', encoding='utf-8') as f:
            json.dump(record, f, ensure_ascii=False, indent=4)

    def store_records(self, records: tp.List[tp.Any]):
        pass
