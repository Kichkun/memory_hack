import os

from parsing.moscow_parser import MoscowParser
from storage.json_storage import JsonStorage

if __name__ == '__main__':
    abs_data_folder = os.path.abspath('./data_new_batch')

    json_storage = JsonStorage(abs_data_folder)

    parser = MoscowParser(abs_data_folder, json_storage)
    parser.parse_ad_hoc(start_from_page=1, end_with_page=40000, cool_down=0.4)

