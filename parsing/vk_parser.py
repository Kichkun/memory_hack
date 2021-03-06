import requests
from json import JSONEncoder
from PIL import Image
from io import BytesIO
#import settings
from crop import crop_chips, get_face_embeddings_from_image, calc_similarity
import time
import cv2
import numpy as np
import re
import json
from urllib.parse import unquote
import os
import shutil
from natasha import NamesExtractor, DatesExtractor
import progressbar


reg_ex = r'[\w-]+.(jpg|png|txt)'
debug = True


class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)


class VKSmallWrapper:

    def __init__(self, token, group_id):
        '''
        :param token: VK Token
        :param group_id: Group id
        '''
        if not token:
            raise ValueError("No `token` specified")

        self.group_id = group_id

        self.version = "5.80"
        self.token = token

        self.api_url = "https://api.vk.com/method/{{}}?access_token={}&v={}" \
            .format(self.token, self.version)

    def execute_api(self, method, params):
        try:
            result = requests.get(self.api_url.format(method), params=params).json()
            return result
        except:
            raise ValueError("Response is not correct!")


def calculate(count):
    count_array = []
    max_val = 100
    offset = 0

    while not count == 0:
        if count >= max_val:
            count_array.append([max_val, offset])
            offset += max_val
            count -= max_val
        else:
            count_array.append([count, offset])
            count -= count

    return count_array


def download_images(name, links, texts):
    print(f"Start downloading {len(links)} images. Wait plz!\n")
    bar = progressbar.ProgressBar(maxval=len(links), widgets=[
        f'Downloading {len(links)} images: ',
        progressbar.Bar(marker='#', left='[', right=']', fill='.'),
        progressbar.Percentage(),
    ]).start()

    if not os.path.exists(f"output/"):
        os.makedirs(f"output/")

    l = 0
    for index, url in enumerate(links):
        l += 1
        bar.update(l)
        result = re.search(reg_ex, url)
        if result:
            g = result.group(0)
        else:
            continue

        img_bytes = requests.get(url, stream=True)
        try:
            if not os.path.exists(f"output/{name}/"):
                os.makedirs(f"output/{name}")
                os.makedirs(f"output/{name}/faces")

            extractor_names = NamesExtractor()
            matches_txt = extractor_names(texts[index])
            names = []

            for match in matches_txt:
                start, stop = match.span
                names.append(texts[index][start:stop])

            extractor_dates = DatesExtractor()
            matches_dates = extractor_dates(texts[index])
            dates = []

            for match in matches_dates:
                start, stop = match.span
                dates.append(texts[index][start:stop])

            meta_dict = {
                    "dates": dates,
                    "author": "VK",
                    "biography": texts[index],
                    "names": names
                    }
            dicti = {"photo_path": f"output/{name}/{g}",
                     "source_url": url,
                     "date": dates[0],
                     "facial_vector": "",
                     "meta": meta_dict
                     }

            with open(f"output/{name}/{g}", 'wb') as f:
                img_bytes.raw.decode_content = True
                shutil.copyfileobj(img_bytes.raw, f)

            im = Image.open(f"output/{name}/{g}")
            image = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)

            res = crop_chips(image, index)

            if res[0] != None:
                if debug:
                    print('faces correct')
                cv2.imwrite(f"output/{name}/faces/face_{g}", res[1])
                dicti['facial_vector'] = json.dumps(res[0], cls=NumpyArrayEncoder)

                with open(f'output/{name}/{g}.json', 'w', encoding='utf-8') as outfile:
                    json.dump(dicti, outfile, indent=4, ensure_ascii=False)

        except Exception as e:
            print(f"ERROR: {e}")

    bar.finish()


def parse_images_from_post(posts):
    links = []
    texts = []

    for post in posts['response']['items']:
        if not post.get("attachments", None):
            continue

        for att in post['attachments']:
            if not att['type'] == "photo":
                continue

            if "sizes" in att['photo']:
                m_s_ind = -1
                m_s_wid = 0

                for i, size in enumerate(att['photo']["sizes"]):
                    if size["width"] > m_s_wid:
                        m_s_wid = size["width"]
                        m_s_ind = i

                link = att['photo']["sizes"][m_s_ind]["url"]
                links.append(link)
                texts.append(post['text'])
            elif "url" in att['photo']:
                link = att['photo']['url']
                links.append(link)
                texts.append(post['text'])

    return links, texts


def get_links(vk_api, count, offset=None):
    counts = calculate(count)
    links = []

    for count in counts:
        params = {
            'owner_id': vk_api.group_id * -1,
            'count': count[0],
            'filter': 'owner'
        }
        if offset:
            params['offset'] = offset + count[1]
        else:
            params['offset'] = count[1]

        res = vk_api.execute_api("wall.get", params)
        l = parse_images_from_post(res)
        for li in l:
            links.append(li)

        time.sleep(5)

    return links


if __name__ == "__main__":
    try:
        v = token
        del (v)
    except:
        raise ValueError("Token is not specified")

    group_id = input("Enter group id\n")

    if not group_id:
        print("Group id is not presented")
        exit()
    elif not group_id.isdigit():
        raise ValueError("Group id is not integer")
    else:
        group_id = int(group_id)

    offset = input("Enter offset is need? (Just enter if not needed)\n")
    if offset and not offset.isdigit():
        raise ValueError("Offset is not integer")
    elif offset:
        offset = int(offset)

    count = input("Enter count of posts with images parse\n")
    if not count:
        print("Count is not presented")
        exit()
    elif not count.isdigit():
        raise ValueError("Count is not integer")
    else:
        count = int(count)

    vk_api = VKSmallWrapper(token, group_id)
    plinks = get_links(vk_api, count, offset)

    download_images(str(vk_api.group_id), plinks[0], plinks[1])
    print("Thanks for using that program!")
