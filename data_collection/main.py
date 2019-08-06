import pandas as pd
from google.cloud import storage
from datetime import datetime
import json
from common import get_domain_from_url, get_base_domain
from google.cloud import pubsub_v1
import DataSource
from DataSource import OpenPhishDataSource, OPENPHISH_URL 
from DataSource import PhishTankDataSource, PHISHTANK_URL
from DataSource import AlexaDataSource, ALEXA_URL, OPENDNS_URL
import hashlib
import cloudstorage as gcs

BUCKET_NAME = 'ground_truth'
project_id = "domain-classifier"
enrich_topic_name = "enrich-domains"
OpenPhish_last_topic_name = "last-collected-OpenPhish"

subscription_name = 'data-collection-OpenPhish'

def collect_data_pubsub(event, context):
    data_source_limit = 1000
    if 'limit' in event:
        data_source_limit = event['limit']
    collect_data(data_source_limit)


def collect_data_http_trigger(request):
    data_source_limit = 1000
    d = request.get_json()
    if 'limit' in d:
        data_source_limit = d['limit']
    collect_data(data_source_limit)

def collect_data(data_source_limit):
    print ('collect_data start')
    # alexa = AlexaDataSource(ALEXA_URL, 'Alexa', 0)
    # opendns = AlexaDataSource(OPENDNS_URL, 'OpenDNS', 0)
    openphish = OpenPhishDataSource(OPENPHISH_URL, 'OpenPhish', 1)
    phishtank = PhishTankDataSource(PHISHTANK_URL, 'PhishTank', 1)
    print ('post create Data Sources')
    current_date_str = datetime.now().strftime("%d-%b-%Y-%H-%M")
    message_columns = ['domain', 'origin', 'label']
    df = pd.DataFrame(columns=message_columns)
    url_df = None
    # for data_source in [alexa, opendns, openphish, phishtank]:
    for data_source in [openphish]:
        origin = data_source.get_origin()
        print (f'handling {origin}')
        url_list = data_source.fetch()
        # client = storage.Client()
        # bucket = client.get_bucket(BUCKET_NAME)
        latest_path = f'{origin}/latest.txt'
        
        # read_blob = bucket.blob(latest_path)
        # latest_url = read_blob.download_as_string(latest_path)

        subscriber = pubsub_v1.SubscriberClient()
        subscription_path = subscriber.subscription_path(project_id, subscription_name)

        # The subscriber pulls a specific number of messages.
        response = subscriber.pull(subscription_path, max_messages=1)
        print ('message pull successfully')
        latest_url = None

        for message in response.received_messages:
            latest_url = message.message.data.decode("utf-8")

        print (f'latest_url: {latest_url}')
        print (f'lastest_path: {latest_path}')
        print (f'url_list[0]: {url_list[0]}')
        if latest_url != url_list[0]:
            # write_blob = bucket.blob(latest_path)
            # write_blob.upload_from_string(url_list[0])
            publisher = pubsub_v1.PublisherClient()
            topic_path = publisher.topic_path(project_id, OpenPhish_last_topic_name)
            publisher.publish(topic_path, data=url_list[0].encode('utf-8'))

            last_url_index = len(url_list)
            if latest_url in url_list:
                last_url_index = url_list.index(latest_url)
            print (f'fetch done. got {len(url_list)} new urls')
            print (f'last_url_index: {last_url_index}')
            url_df = pd.DataFrame(url_list[:min(data_source_limit, last_url_index)], columns=['url'])
            print (f'{origin} df length: {len(url_df)}')
        
        if url_df and len(url_df) > 0:
            url_df.to_csv(f'gs://{BUCKET_NAME}/{data_source.get_origin()}/{current_date_str}.txt')
        else:
            print ('no new urls to upload.')

        url_df.loc[:, 'domain'] = url_df['url'].apply(get_domain_from_url)
        url_df['label'] = data_source.get_label()
        url_df['origin'] = data_source.get_origin()
        
        df = pd.concat([df, url_df[message_columns]])

    df.loc[:, 'base_domain'] = df['domain'].apply(get_base_domain)
    df.drop_duplicates(subset=['base_domain'], inplace=True)
    print (f'total df length: {len(df)}')
    df = df.reset_index()
    push_df_to_pubsub(project_id, enrich_topic_name, df[message_columns])
    return 'Done.'

    

def push_df_to_pubsub(project_id, topic_name, df):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_name)
    for start_index in range(0, len(df), 25):    
        json_data = df[start_index : start_index + 25].T.to_json()
        print (json_data)
        publisher.publish(topic_path, data=json_data.encode('utf-8'))
