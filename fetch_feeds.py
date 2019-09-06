import pandas as pd
from google.cloud import storage
from datetime import datetime
import json
from common import get_domain_from_url, get_base_domain
import DataSource
from DataSource import OpenPhishDataSource, OPENPHISH_URL, OPENPHISH_STR, NEW_URL_TOPIC
from DataSource import PhishTankDataSource, PHISHTANK_URL, PHISHTANK_STR
from DataSource import AlexaDataSource, ALEXA_URL, ALEXA_STR
from DataSource import OPENDNS_URL, OPENDNS_STR
from redis import StrictRedis
import os
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-source", type=str, help="datasource to fetch")
    parser.add_argument("--redis-host", type=str, default='localhost', help="redis hostname")
    parser.add_argument("--redis-port", type=int, default=6379, help="redis port")
    parser.add_argument("--redis-db", type=int, default=0, help="redis db index")
    parser.add_argument("--publish-limit", type=int, default=10000, help="publish limit for fetched URLS")
    args = parser.parse_args()

    print ('main start')
    redis = StrictRedis(host=args.redis_host, port=args.redis_port, db=args.redis_db)

    # phishtank_url = PHISHTANK_URL.format(apikey=phishtank_apikey)
    # print (f'phishtank_url: {phishtank_url}')
    # openphish = OpenPhishDataSource(OPENPHISH_URL, 'OpenPhish', 1, PHISHING_URL_TOPIC, None)
    # phishtank = PhishTankDataSource(phishtank_url, 'PhishTank', 1, PHISHING_URL_TOPIC, None)
    data_source_arg = args.data_source.lower()
    data_source = None
    if data_source_arg == OPENPHISH_STR.lower():
        data_source = OpenPhishDataSource(OPENPHISH_URL, OPENPHISH_STR, 1, NEW_URL_TOPIC, None)

    elif data_source_arg == PHISHTANK_STR.lower():
        phishtank_apikey = ''
        if 'PHISHTANK_APIKEY' in os.environ:
            phishtank_apikey = os.getenv('PHISHTANK_APIKEY')
        phishtank_url = PHISHTANK_URL.format(apikey=phishtank_apikey)
        data_source = PhishTankDataSource(phishtank_url, PHISHTANK_STR, 1, NEW_URL_TOPIC, None)

    elif data_source_arg == ALEXA_STR.lower():
        data_source = AlexaDataSource(ALEXA_URL, ALEXA_STR, 0, NEW_URL_TOPIC, None)

    elif data_source_arg == OPENDNS_STR.lower():
        data_source = AlexaDataSource(OPENDNS_URL, OPENDNS_STR, 0, NEW_URL_TOPIC, None)



    if data_source:
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
            for url in url_list[:min(last_url_index, args.publish_limit)]:
                message = json.dumps({'url': url, 'label': data_source.get_label()})
                redis.publish(data_source.get_topic(), message)
            print (f'update latest url  of {origin} to: {url_list[0]}')
            redis.set(origin, url_list[0], ex=86400)

if __name__ == "__main__":
    main()