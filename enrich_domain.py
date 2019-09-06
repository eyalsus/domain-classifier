import pandas as pd
# from google.cloud import storage
from datetime import datetime
import json
from common import get_domain_from_url, get_base_domain
from DataSource import NEW_URL_TOPIC, ENRICHED_DOMAIN
import os
from FeatureExtraction import feature_extractor
from redis import StrictRedis
import json


def main():
    print ('main start')
    redis = StrictRedis(host='localhost', port=6379, db=0)
    pubsub = redis.pubsub()
    pubsub.subscribe(NEW_URL_TOPIC)
    print ('start listening...')
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
                    print(f'published {domain} to channel {ENRICHED_DOMAIN}')
        except Exception as e:
            print(message, e)

if __name__ == "__main__":
    main()