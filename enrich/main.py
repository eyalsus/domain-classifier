import pandas as pd
from FeatureExtraction import feature_extractor
from google.cloud import storage
from datetime import datetime
import json
import base64

BUCKET_NAME = 'ground_truth'
project_id = "domain-classifier"
topic_name = "data_collection"

# def main():
#     feature_extraction = FeatureExtraction()
#     alexa_df = pd.read_csv('resources/top-1m.csv', names=['rank', 'domain'])
#     domain_list = alexa_df['domain'][:100]
#     df = feature_extraction.extract(domain_list, label=0)
#     # df.to_csv('top_benign.csv', index=False)

#     # upload_file_to_bucket('ground_truth', 'Alexa', 'test', 'D:\\projects\\domain-classifier\\Alexa.csv')


#     return


#     df = pd.read_csv('top_benign.csv')
#     domain_list = df['domain'][:500]

#     sna = SocialNetworkAnalysis()
#     df.apply(sna.append_row_to_graph, axis=1)

    

#     # for domain in domain_list:
#     #     print(domain, sna.G.nodes[domain]['current'])

#     print('------------------------------------------------------------------')

#     sna.stable_graph()
#     for domain in domain_list:
#         print(domain, sna.G.nodes[domain]['current'])

#     print (len(sna.G))



def domains_feature_extraction_pubsub(event, context):
    d = json.loads(base64.b64decode(event['data']))
    current_date_str = datetime.now().strftime("%d-%b-%Y-%H-%M-%S")    
    message_df = pd.DataFrame.from_dict(d.values())
    df = feature_extractor.extract(message_df)
    print (f'putting {len(df)} to bucket')
    df.to_csv(f'gs://{BUCKET_NAME}/GT/{current_date_str}.txt')
    print (f'domains_feature_extraction_pubsub done')
    return 'Done.'


# # def test_storage(request):
# #     d = request.get_json()
# #     upload_file_to_bucket(d['bucket_name'], d['bucket_path'])

# # def upload_df_to_bucket(df, bucket_name, blob_path):
# #     client = storage.Client()
# #     bucket = client.get_bucket(bucket_name)
    
# #     blob = bucket.blob(blob_path)
# #     byte_buff = BytesIO()
# #     with open(byte_buff, 'r') as f:
# #         df.to_pickle(byte_buff, compression=None):
# #         blob.upload_from_file(f)

# if __name__ == "__main__":
#     main()