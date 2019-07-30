import requests
import pandas as pd
from io import StringIO

OPENPHISH_URL = 'https://openphish.com/feed.txt'
PHISHTANK_URL = 'http://data.phishtank.com/data/online-valid.csv'

class DataSource(object):
    
    def __init__(self, url):
        self.url = url
    

    def get_data_source_name(self):
        pass


    def fetch(self):
        pass


class PhishTankDataSource(DataSource):
    
    def __init__(self, url):
        super().__init__(url)


    def get_data_source_name(self):
        return "PhishTank"


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
    
    
    def fetch(self):
        url_list = []
        res = requests.get(self.url)
        if res.status_code == 200:
            url_list = res.text.split('\n')
        return url_list


        