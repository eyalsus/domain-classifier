import requests
import pandas as pd
from io import StringIO, BytesIO
from zipfile import ZipFile

OPENPHISH_URL = 'https://openphish.com/feed.txt'
PHISHTANK_URL = 'http://data.phishtank.com/data/online-valid.csv'
ALEXA_URL = 'http://s3.amazonaws.com/alexa-static/top-1m.csv.zip'
OPENDNS_URL = 'http://s3-us-west-1.amazonaws.com/umbrella-static/top-1m.csv.zip'

class DataSource(object):
    
    def __init__(self, url, origin, label):
        self._url = url
        self._origin = origin
        self._label = label
    

    def get_origin(self):
        return self._origin


    def get_label(self):
        return self._label


    def fetch(self):
        pass

class AlexaDataSource(DataSource): 
    def __init__(self, url, origin, label):
        super().__init__(url, origin, label)


    def fetch(self):
        url_list = []
        res = requests.get(self._url)
        if res.status_code == 200:
            with ZipFile(BytesIO(res.content)) as zipfile:
                for contained_file in zipfile.namelist():
                    for line in zipfile.open(contained_file).readlines():
                        url_list.append(line.decode("utf-8").split(',')[1][:-1])
        return url_list


class PhishTankDataSource(DataSource):
    
    def __init__(self, url, origin, label):
        super().__init__(url, origin, label)


    def fetch(self):
        url_list = []
        res = requests.get(self._url)
        if res.status_code == 200:
            data = StringIO(res.text)
            df = pd.read_csv(data)
            url_list = list(df['url'])
        return url_list


class OpenPhishDataSource(DataSource):

    def __init__(self, url, origin, label):
        super().__init__(url, origin, label)


    def fetch(self):
        url_list = []
        res = requests.get(self._url)
        if res.status_code == 200:
            url_list = res.text.split('\n')
        return url_list


        