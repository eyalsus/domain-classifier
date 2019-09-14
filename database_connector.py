from sqlalchemy import create_engine
import pandas as pd
from time import sleep
from redis import StrictRedis
from DataSource import ENRICHED_DOMAIN
import json
import os
import logging
from datetime import datetime

# create logger with 'spam_application'
logger = logging.getLogger('database_connector')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
log_dir_path = os.getenv('LOG_DIR_PATH')
date_str = datetime.now().isoformat().replace(':', '_').split('.')[0]
log_file_name = f'database_connector_{date_str}.log'
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
            if message['type'] == 'message':
                
                entry = pd.read_sql(f"select count(1) from domains where domain = '{domain.decode('ascii')}'", engine)
                if entry['count'][0] == 1:
                    logger.info(f'{domain} already exists in the DB')
                else:
                    logger.info(f'get data from redis from domain {domain}')
                    features = redis.get(domain)
                    if features:
                        commit_batch.append(json.loads(features))
                
                    logger.info(f'len(commit_batch): {len(commit_batch)}')
                    if len(commit_batch) >= COMMIT_BATCH_SIZE:
                        df = pd.DataFrame.from_dict(commit_batch)
                        df['timestamp'] = df['timestamp'].apply(pd.to_datetime)
                        df.to_sql('domains', engine, if_exists='append', index=False)
                        logger.info('wrote commit_batch to DB')
                        commit_batch.clear()
        except:
            logger.info(message)


if __name__ == "__main__":
    main()