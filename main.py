import json
import time
from pprint import pprint
import requests as requests
from tqdm import tqdm

class OK:
    url = 'https://api.ok.ru/fb.do'
    anchor_ = ''
    hasMore = True
    time_list = []
    rez_dict = {}

    def __init__(self, user_id):
        self.key = open('tokens.txt').readlines()[1].strip('\n')
        self.token = open('tokens.txt').readlines()[3].strip('\n')
        self.secret_key = open('tokens.txt').readlines()[5].strip('\n')
        self.user_id = user_id


    def get_photo(self, count_):
        params = {'application_key': self.key,
                 'detectTotalCount': 'true',
                 'fid': self.user_id,
                 'method': 'photos.getPhotos',
                 'format': 'json',
                  'direction': 'FORWARD',
                  'count': count_,
                  'anchor': self.anchor_,
                  'fields': 'photo.LIKE_COUNT, photo.PHOTO_ID, photo.PIC_MAX, photo.CREATED_MS',
                 'access_token': self.token}
        resp = requests.get(self.url, params=params)
        self.anchor_ = resp.json()['anchor']
        self.hasMore = resp.json()['hasMore']
        self.link_for_upload = [photo['pic_max'] for photo in resp.json()['photos']]
        self.like_for_pfoto = [photo['like_count'] for photo in resp.json()['photos']]
        self.unix_time_ = [int(float(photo['created_ms']) * 0.001) for photo in resp.json()['photos']]
        self.local_time_ = [time.strftime("%d_%b_%Y_%H_%M_%S", time.localtime(time_)) for time_ in self.unix_time_]
        self.time_list = list(zip(self.like_for_pfoto, self.local_time_))
        self.rez_dict = dict(zip(self.link_for_upload, self.time_list))


        return resp.json()

class YaDisk:
    url_ = 'https://cloud-api.yandex.net/v1/disk/resources/upload'

    def __init__(self):
        self.ya_token = open('tokens.txt').readlines()[7].strip('\n')
        self.headers = {'Content-Type': 'application/json',
                        'Authorization': f'OAuth {self.ya_token}'
                        }

    def upload_photo_from_internet(self, rez_):
        self.g = []
        self.full_path_ = ''

        for link_, like_set in tqdm(rez_.items()):
            time.sleep(0.2)
            self.link_ = link_
            self.like_ = f'{like_set[0]}'
            self.date_ = like_set[1]

            if self.like_ not in self.g:
                self.g.append(f'{self.like_}')
                self.full_path_ = f'/img/{self.like_}'
            else:
                self.full_path_ = f'/img/{self.like_}_{self.date_}'


            params = {'url': self.link_,
                      'path': self.full_path_
                      }
            self.response = requests.post(url=self.url_, params=params, headers=self.headers)

            self.response.raise_for_status()


if __name__=='__main__':
    try:
        ok_ = OK(input('Введите ID пользователя: '))
        ok_.get_photo(int(input('Введите количество фото для перемещения: ')))
        ya_ = YaDisk()
        ya_.upload_photo_from_internet(ok_.rez_dict)
    except IndexError as ind_err:
        pprint(f'ERROR - {ind_err}')
    except ValueError as err:
        pprint(f'ERROR - Данные должны быть целым числом - {err}')
    except Exception as err:
        pprint(f'ERROR - {err}')




