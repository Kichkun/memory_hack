import os
from typing import List, Optional, Dict
import requests
from lxml import html
import tqdm
import time
from urllib.parse import urljoin

from parser.abstract import AbstractParser
from storage.json_storage import JsonStorage

import random
import string


def random_str(str_len=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(str_len))


def save_img_from_url(url, path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(path, 'wb') as f:
            f.write(response.content)
        return path
    return None


class MoscowParser(AbstractParser):
    __URL_BASE = 'https://www.polkmoskva.ru/'
    __URL_PEOPLE = 'https://www.polkmoskva.ru/people/'
    __URL_PEOPLE_SEARCH_TEMPLATE = 'https://www.polkmoskva.ru/veteran_search/?PAGEN_2={}'

    def __init__(self, dir_to_save: str, storage_model: JsonStorage, people_urls: Optional[List] = None):
        super().__init__(dir_to_save, storage_model)
        self._people_urls = people_urls

    def parse(self):
        if not self._people_urls:
            self._people_urls = MoscowParser.extract_people_pages()

        for url in self._people_urls:
            try:
                extracted_data = self.__extract_data(url)
                self.storage_model.store_record(extracted_data)

            except Exception:
                continue
        time.sleep(0.1)

    def parse_ad_hoc(self, start_from_page, end_with_page, cool_down=0.3):
        self._people_urls = []

        for i in tqdm.tqdm(range(start_from_page, end_with_page+1)):
            url = MoscowParser.__URL_PEOPLE_SEARCH_TEMPLATE.format(i)
            content = requests.get(url).content
            tree = html.fromstring(content.decode())
            links = tree.xpath('//div[@class="b-veteranList-item__headTitle"]/a')
            self._people_urls = [urljoin(MoscowParser.__URL_BASE, x.get('href')) for x in links]
            self.parse()
            if cool_down > 0:
                time.sleep(cool_down)

    def __extract_data(self, url):
        content = requests.get(url).content
        tree = html.fromstring(content.decode())

        img_relative_url = tree.xpath('//img[@class="b-veteranInfo__asideImg"]')[0].get('src')
        img_absolute_url = urljoin(MoscowParser.__URL_BASE, img_relative_url)
        name = tree.xpath('//h1')[0].text_content().strip()
        date_element = tree.xpath("//div[@class='b-veteranInfo__birthday']")
        birth_element = tree.xpath("//div[@class='b-veteranInfo__item b-veteranInfo__birthplace']")
        return {
            'source_url': url,
            'name': name,
            'date': date_element[0].text_content().strip() if date_element else None,
            'place_of_birth': birth_element[0].text_content().replace('Меcто рождения:', '').strip()
            if birth_element else None,
            'general_military_info':
                MoscowParser.__extract_military_attributes(tree.xpath('//div[@class="b-veteranInfo__item"]')),
            'medals': [x.text_content().strip() for x in tree.xpath('//div[@class="b-veteranHonors-item__title"]')],
            'img_path': save_img_from_url(img_absolute_url, f'{self.dir_to_save}/{name}.png'),
            'img_url': img_absolute_url,
            'side_media_urls': list(set(urljoin(MoscowParser.__URL_BASE, x.get('src')) for x in
                                        tree.xpath('//div[@class="b-photoGallery__listWrap"]/img'))),
            'biography': MoscowParser.__extract_biography(tree.xpath('//div[@class="b-article"]')),
            'member_of_battles': MoscowParser.__extract_battle_info(tree.xpath('//ul[@class="b-veteranBattle__list"]'))
        }

    @classmethod
    def __extract_military_attributes(cls, info) -> Dict[str, str]:
        attributes = {}
        for piece in info:
            piece = piece.text_content().strip()
            title, data = piece.split(':')
            attributes[title.strip()] = data.strip()  # convert to english ?
        return attributes

    @classmethod
    def __extract_biography(cls, info) -> Dict[str, str]:
        biography = {}
        for piece in info:
            title = piece[0].text_content().strip()
            describe = piece[1].text_content().strip()
            biography[title] = describe
        return biography

    @classmethod
    def __extract_battle_info(cls, info) -> List[str]:
        battles = info[0].getchildren() if info else []
        battles = [x.text_content().strip() for x in battles]
        return battles

    @classmethod
    def extract_people_pages(cls, save_to_file_path: str = None, start_from_page: int = 1) -> Optional[List]:
        parsed_pages = []

        for i in tqdm.tqdm(range(start_from_page, 41791)):
            url = MoscowParser.__URL_PEOPLE_SEARCH_TEMPLATE.format(i)
            content = requests.get(url).content
            tree = html.fromstring(content.decode())
            links = tree.xpath('//div[@class="b-veteranList-item__headTitle"]/a')
            parsed_pages.extend([urljoin(MoscowParser.__URL_BASE, x.get('href')) for x in links])
            if i % 5 == 0:
                time.sleep(0.3)

        if save_to_file_path:
            with open(save_to_file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(parsed_pages))
        return parsed_pages


if __name__ == '__main__':
    abs_data_folder = os.path.abspath('./data_20000_30000')

    json_storage = JsonStorage(abs_data_folder)

    parser = MoscowParser(abs_data_folder, json_storage)
    parser.parse_ad_hoc(start_from_page=1, end_with_page=1, cool_down=0.3)
