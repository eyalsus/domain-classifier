import pandas as pd
from google.cloud import storage
from datetime import datetime
import json
from common import get_domain_from_url, get_base_domain
import DataSource
from DataSource import OpenPhishDataSource, OPENPHISH_URL 
from DataSource import PhishTankDataSource, PHISHTANK_URL
from DataSource import AlexaDataSource, ALEXA_URL, OPENDNS_URL, PHISHING_URL_TOPIC
from redis import StrictRedis
import os


def main():
    print ('main start')
    redis = StrictRedis(host='localhost', port=6379, db=0)

    phishtank_apikey = ''
    if 'PHISHTANK_APIKEY' in os.environ:
        phishtank_apikey = os.getenv('PHISHTANK_APIKEY')
    phishtank_url = PHISHTANK_URL.format(apikey=phishtank_apikey)
    print (f'phishtank_url: {phishtank_url}')
    openphish = OpenPhishDataSource(OPENPHISH_URL, 'OpenPhish', 1, PHISHING_URL_TOPIC, None)
    phishtank = PhishTankDataSource(phishtank_url, 'PhishTank', 1, PHISHING_URL_TOPIC, None)

    for data_source in [openphish, phishtank]:
        origin = data_source.get_origin()
        print (f'handling {origin}')
        url_list = data_source.fetch()
        print (f'len(url_list): {len(url_list)}')
        print (f'url_list[0]: {url_list[0]}')
        
        latest_url = redis.get(origin)

        if latest_url:
            latest_url = latest_url.decode('utf-8')

        print (f'latest_url (from redis): {latest_url}')

        if latest_url is None or latest_url != url_list[0]:
            last_url_index = len(url_list)
            if latest_url in url_list:
                last_url_index = url_list.index(latest_url)
            print (f'fetch done. got {len(url_list)} new urls')
            print (f'last_url_index: {last_url_index}')
            for url in url_list[:last_url_index]:
                message = json.dumps({'url': url, 'label': data_source.get_label()})
                redis.publish(data_source.get_topic(), message)
            print (f'update latest url  of {origin} to: {url_list[0]}')
            redis.set(origin, url_list[0], ex=86400)

if __name__ == "__main__":
    main()