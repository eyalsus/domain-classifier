import pandas as pd
# from google.cloud import storage
from datetime import datetime
import json
from common import get_domain_from_url, get_base_domain
from DataSource import NEW_URL_TOPIC, ENRICHED_DOMAIN
from FeatureExtraction import feature_extractor
from redis import StrictRedis
import json
import os
import logging
from datetime import datetime

logger = logging.getLogger('enrich_domain')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
log_dir_path = os.getenv('LOG_DIR_PATH')
date_str = datetime.now().isoformat().replace(':', '_').split('.')[0]
log_file_name = f'enrich_domain_{date_str}.log'
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
logger.info('logger is ready!')

def main():
    logger.info('main start')
    print('main start print')
    redis = StrictRedis(host='localhost', port=6379, db=0)
    pubsub = redis.pubsub()
    pubsub.subscribe(NEW_URL_TOPIC)
    logger.info('going into listening mode...')
    for message in pubsub.listen():
        try:
            if message['type'] == 'message':
                message_content = json.loads(message['data'])
                url = message_content['url'] #.decode('utf-8')
                label = message_content['label']
                domain = get_domain_from_url(url)
                if domain and not redis.get(domain):
                    features = feature_extractor.extract_domain_features(domain, label)
                    redis.set(domain, json.dumps(features), ex=7200)
                    redis.publish(ENRICHED_DOMAIN, domain)
                    logger.info(f'published {domain} to channel {ENRICHED_DOMAIN}')
        except:
            logger.error(message)

if __name__ == "__main__":
    main()