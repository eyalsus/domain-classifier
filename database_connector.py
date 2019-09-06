from sqlalchemy import create_engine
import pandas as pd
from time import sleep
from redis import StrictRedis
from DataSource import ENRICHED_DOMAIN
import json

COMMIT_BATCH_SIZE = 10

def main():
    
    redis = StrictRedis(host='localhost', port=6379, db=0)                        
    engine = create_engine('postgresql://postgres:mypassword@localhost:5432/')
    pubsub = redis.pubsub()                                                        
    pubsub.subscribe(ENRICHED_DOMAIN)
    commit_batch = []                             
    for message in pubsub.listen():
        try:
            domain = message['data']
            print(f'get data from redis from domain {domain}')
            entry = pd.read_sql(f"select count(1) from domains where domain = '{domain}'", engine)
            if entry['count'][0] == 1:
                print (f'{domain} already exists in the DB')
            else:
                features = redis.get(domain)
                if features:
                    commit_batch.append(json.loads(features))
            
                print (f'len(commit_batch): {len(commit_batch)}')
                if len(commit_batch) >= COMMIT_BATCH_SIZE:
                    df = pd.DataFrame.from_dict(commit_batch)
                    df['timestamp'] = df['timestamp'].apply(pd.to_datetime)
                    df.to_sql('domains', engine, if_exists='append', index=False)
                    print ('wrote commit_batch to DB')
                    commit_batch.clear()
        except Exception as e:
            print(message, e)


if __name__ == "__main__":
    main()