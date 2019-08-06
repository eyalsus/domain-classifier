print('start!')
import DataSource
from DataSource import OpenPhishDataSource, OPENPHISH_URL 
from DataSource import PhishTankDataSource, PHISHTANK_URL
from DataSource import AlexaDataSource, ALEXA_URL, OPENDNS_URL
from FeatureExtraction import feature_extractor
from datetime import date
from google.cloud import storage
import json
import pandas as pd
from common import get_domain_from_url, get_base_domain
from google.cloud import pubsub_v1



print('Finished loading imports!')

BUCKET_NAME = 'ground_truth'
project_id = "domain-classifier"
topic_name = "data_collection"

def collect_data():
    alexa = AlexaDataSource(ALEXA_URL, 'Alexa', 0)
    opendns = AlexaDataSource(OPENDNS_URL, 'OpenDNS', 0)
    openphish = OpenPhishDataSource(OPENPHISH_URL, 'OpenPhish', 1)
    phishtank = PhishTankDataSource(PHISHTANK_URL, 'PhishTank', 1)
    
    current_date_str = date.today().strftime("%d-%b-%Y")
    message_columns = ['domain', 'origin', 'label']
    df = pd.DataFrame(columns=message_columns)

    for data_source in [alexa, opendns, openphish, phishtank]:
        url_list = data_source.fetch()
        url_df = pd.DataFrame(url_list[:50000], columns=['url'])
        print (f'{data_source.get_origin()} df length: {len(url_df)}')
        url_df.to_csv(f'gs://{BUCKET_NAME}/{data_source.get_origin()}/raw_data/{current_date_str}.csv')

        url_df.loc[:, 'domain'] = url_df['url'].apply(get_domain_from_url)
        url_df['label'] = data_source.get_label()
        url_df['origin'] = data_source.get_origin()
        
        df = pd.concat([df, url_df[message_columns]])

    df.loc[:, 'base_domain'] = df['domain'].apply(get_base_domain)
    df.drop_duplicates(subset=['base_domain'], inplace=True)
    print (f'total df length: {len(df)}')
    df = df.reset_index()
    json_data = df[message_columns].T.to_json()
    print (json_data)
    push_data_to_pubsub(project_id, topic_name, json_data)


def push_data_to_pubsub(project_id, topic_name, json_data):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_name)
    publisher.publish(topic_path, data=json_data.encode('utf-8'))


def full_test():
    openphish = OpenPhishDataSource(OPENPHISH_URL, 'OpenPhish', 1)
    phishtank = PhishTankDataSource(PHISHTANK_URL, 'PhishTank', 1)
    alexa = AlexaDataSource(ALEXA_URL, 'Alexa', 0)
    opendns = AlexaDataSource(OPENDNS_URL, 'OpenDNS', 0)

    print('Build data sources!')
    current_date_str = date.today().strftime("%d-%b-%Y")

    for data_source in [openphish, phishtank, alexa, opendns]:
        url_list = data_source.fetch()
        print (len(url_list))
        df = feature_extractor.extract(url_list[:100], data_source.get_origin(),data_source.get_label())
        print (len(df))
        df.to_csv(f'{data_source.get_origin()}-{current_date_str}.csv')
        # df.to_csv(f'gs://{BUCKET_NAME}/{data_source.get_name()}/{current_date_str}.csv')
        # df.to_parquet(f'gs://ground_truth/{data_source.get_data_source_name()}/{current_date_str}.parquet.gzip', compression='gzip')


collect_data()