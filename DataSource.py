import requests
import pandas as pd
from io import StringIO, BytesIO
from zipfile import ZipFile

OPENPHISH_URL = 'https://openphish.com/feed.txt'
PHISHTANK_URL = 'http://data.phishtank.com/data/online-valid.csv'
Alexa_URL = 'http://s3.amazonaws.com/alexa-static/top-1m.csv.zip'

class DataSource(object):
    
    def __init__(self, url):
        self.url = url
    

    def get_data_source_name(self):
        pass


    def get_data_source_label(self):
        pass


    def fetch(self):
        pass

class AlexaDataSource(DataSource): 
    def __init__(self, url):
        super().__init__(url)


    def get_data_source_name(self):
        return "Alexa"


    def get_data_source_label(self):
        return 0


    def fetch(self):
        url_list = []
        res = requests.get(self.url)
        if res.status_code == 200:
            with ZipFile(BytesIO(res.content)) as zipfile:
                for contained_file in zipfile.namelist():
                    for line in zipfile.open(contained_file).readlines():
                        url_list.append(line.decode("utf-8").split(',')[1][:-1])
        return url_list


class PhishTankDataSource(DataSource):
    
    def __init__(self, url):
        super().__init__(url)


    def get_data_source_name(self):
        return "PhishTank"

    
    def get_data_source_label(self):
        return 1


    def fetch(self):
        url_list = []
        res = requests.get(self.url)
        if res.status_code == 200:
            data = StringIO(res.text)
            df = pd.read_csv(data)
            print (df.columns)
            url_list = list(df['url'])
        return url_list


class OpenPhishDataSource(DataSource):

    def __init__(self, url):
        super().__init__(url)

    
    def get_data_source_name(self):
        return "OpenPhish"
    

    def get_data_source_label(self):
        return 1


    def fetch(self):
        url_list = []
        res = requests.get(self.url)
        if res.status_code == 200:
            url_list = res.text.split('\n')
        return url_list


        