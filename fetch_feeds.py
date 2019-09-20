import json
from common import get_domain_from_url, get_base_domain
import DataSource
from DataSource import OpenPhishDataSource, OPENPHISH_URL, OPENPHISH_STR, NEW_URL_TOPIC
from DataSource import PhishTankDataSource, PHISHTANK_URL, PHISHTANK_STR
from DataSource import AlexaDataSource, ALEXA_URL, ALEXA_STR
from DataSource import OPENDNS_URL, OPENDNS_STR
from redis import StrictRedis
from time import sleep
import argparse
import os
import logging
from datetime import datetime

logger = None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--infinity", action='store_true')
    parser.add_argument("--data-source", type=str, help="datasource to fetch")
    parser.add_argument("--redis-host", type=str, default='localhost', help="redis hostname")
    parser.add_argument("--redis-port", type=int, default=6379, help="redis port")
    parser.add_argument("--redis-db", type=int, default=0, help="redis db index")
    parser.add_argument("--publish-limit", type=int, default=10000, help="publish limit for fetched URLS")
    args = parser.parse_args()
    print (args)
    # phishtank_url = PHISHTANK_URL.format(apikey=phishtank_apikey)
    # logger.info(f'phishtank_url: {phishtank_url}')
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
    
    print (f'data_source: {data_source.get_origin}')
    global logger
    logger = define_logger(data_source.get_origin())
    logger.info(f'program args: {args}')

    while(True):
        redis = StrictRedis(host=args.redis_host, port=args.redis_port, db=args.redis_db)
        fetch_feed(data_source, args.publish_limit, redis)
        if not args.infinity:
            break
        sleep_duration = int(os.getenv('FETCH_SLEEP_TIME'))
        logger.info(f'going to sleep now for {sleep_duration} seconds...')
        sleep(sleep_duration)
        logger.info('woke up!')


def fetch_feed(data_source, publish_limit, redis):
    if data_source:
        origin = data_source.get_origin()
        logger.info(f'handling {origin}')
        url_list = data_source.fetch()
        logger.info(f'len(url_list): {len(url_list)}')
        logger.info(f'url_list[0]: {url_list[0]}')
        
        latest_url = redis.get(origin)

        if latest_url:
            latest_url = latest_url.decode('utf-8')

        logger.info(f'latest_url (from redis): {latest_url}')

        if latest_url is None or latest_url != url_list[0]:
            last_url_index = len(url_list)
            if latest_url in url_list:
                last_url_index = url_list.index(latest_url)
            logger.info(f'fetch done. got {len(url_list)} new urls')
            logger.info(f'last_url_index: {last_url_index}')
            for url in url_list[:min(last_url_index, publish_limit)]:
                message = json.dumps({'url': url, 'label': data_source.get_label()})
                redis.publish(data_source.get_topic(), message)
            logger.info(f'update latest url of {origin} to: {url_list[0]}')
            redis.set(origin, url_list[0], ex=86400)

def define_logger(data_source_name):
    logger = logging.getLogger(f'fetch_{data_source_name}')
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    log_dir_path = os.getenv('LOG_DIR_PATH')
    date_str = datetime.now().isoformat().replace(':', '_').split('.')[0]
    log_file_name = f'fetch_{data_source_name}_{date_str}.log'
    log_file_path = os.path.join(log_dir_path, log_file_name)
    fh = logging.FileHandler(log_file_path)
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


if __name__ == "__main__":
    main()
