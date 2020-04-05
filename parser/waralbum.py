from json import JSONEncoder

import numpy as np
import cv2
from PIL import Image
from io import BytesIO
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import tqdm
import sys
from crop import crop_chips, get_face_embeddings_from_image, calc_similarity

chrome_options = Options()
chrome_options.headless = True
driver = webdriver.Chrome("/home/ksihkun/.wdm/drivers/chromedriver/78.0.3904.105/linux64/chromedriver",
                          options=chrome_options)

start = 352
bias = 300000
debug = False
root_url = 'http://waralbum.ru/'
stop_words = ['немецких', 'Германии']

class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)

for i in tqdm.tqdm(range(start, start + bias), file = sys.stdout):
    out = {}

    data = f'{root_url}{i}'
    driver.get(data)

    text_out = ""
    out['category'] = []
    try:
        work = True
        els = driver.find_elements_by_css_selector("a[rel='category tag']")
        #print(els[0].text, els[1].text)
        for d, el in enumerate(els):
            #hr = els[i].get_attribute('href')
            out['category'].append(els[d].text)
            for st in stop_words:
                if st in els[d].text:
                    work = False
        print(out['category'])
        if work:
            if debug:
                print('category correct')
            elem_name = driver.find_element_by_class_name('title')
            if debug:
                print('title correct')
            out['title'] = elem_name.text
            if 'Ошибка 404' not in elem_name.text:
                photo = driver.find_elements_by_tag_name('img')
                if debug:
                    print('img correct')
                src_2 = ''
                for ph in photo:
                    try:
                        if 'photocache' in ph.get_attribute('src'):
                            src_2 = ph.get_attribute('src')
                            break
                    except:
                        pass
                if 'photocache' in src_2:
                    if debug:
                        print('photo correct')
                    out['img'] = src_2
                    text = driver.find_elements_by_tag_name('p')
                    flag = False
                    out['sources'] = []
                    for el in text:
                        if el.text !='':
                            if not flag:
                                text_out += el.text
                                flag = True
                            #else:
                            #    for sp in el.text.split('\n'):
                            #        out['sources'].append(sp)
                    out['fulltext'] = text_out
                    out['source_url'] = data
                    if debug:
                        print('text correct')
                    text = driver.find_elements_by_tag_name('li')
                    out['place'] = ''
                    out['datetime'] = ''
                    out['author'] = ''
                    for el in text:
                        if 'Место' in el.text:
                            out['place'] = el.text.split(': ')[1]
                        if 'Время' in el.text:
                            out['datetime'] = el.text.split(': ')[1]
                        if 'Автор' in el.text:
                            out['author'] = el.text.split(': ')[1]

                    out['name'] = ''
                    print(out)
                    if debug:
                        print('eth correct')


                    image_name = f'./wow/{i}.png'

                    driver.get(src_2)
                    png = driver.get_screenshot_as_png()
                    im = Image.open(BytesIO(png))
                    image = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)

                    res = crop_chips(image, i)

                    if res != None:
                        if debug:
                            print('faces correct')
                        im.save(image_name)
                        out['descriptors'] = json.dumps(res, cls=NumpyArrayEncoder)
                        path = f'./wow/{i}.json'
                        path_des = f'./wow/{i}_des.json'
                        print(out)
                        with open(path, 'w', encoding='utf-8') as outfile:
                            json.dump(out, outfile, ensure_ascii=False)

    except:
        print('error', i)
