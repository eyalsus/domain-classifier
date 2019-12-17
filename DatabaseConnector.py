from sqlalchemy import create_engine
import pandas as pd
from redis import StrictRedis
import json
import logging
import sys

COMMIT_BATCH_SIZE = 10
CONNECTION_STRING = 'postgresql://postgres:mypassword@localhost:5432/'
HOSTING_QUERY = "AND base_domain NOT IN ('000webhostapp.com', 'azurewebsites.net', 'duckdns.org', 'no-ip.com', 'no-ip.org', 'wixsite.com')"
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

class DatabaseConnector(object):
    def __init__(self, logger=None):
        self.set_logger(logger)
        self.commit_batch = []
        self.engine = create_engine(CONNECTION_STRING)
        self.redis = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

    def set_logger(self, logger):
        if logger:
            self.logger = logger
        else:
            logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
            self.logger = logging

    def is_domain_record_exist(self, domain):
        """[check of domain already exist in the DB]
        
        Arguments:
            domain {[str]} -- [domain to check if is in DB]
        
        Returns:
            [bool] -- [boolean answer is domain in DB]
        """
        if isinstance(domain, bytes):
            domain = domain.decode('ascii')
        entry = pd.read_sql_query(f"select count(1) from domains where domain = '{domain}'", self.engine)
        return entry['count'][0] == 1

    def add_domain_to_db(self, domain):
        """[add given domain to the DB]
        
        Arguments:
            domain {[str]} -- [domain to add the DB]
        
        Returns:
            [int] -- [amount of domain actually added to the DB]
        """
        res = 0
        self.logger.info('get data from redis from domain %s', domain)
        features = self.redis.get(domain)
        if features:
            self.commit_batch.append(json.loads(features))

        self.logger.info('len(commit_batch): %d', len(self.commit_batch))
        if len(self.commit_batch) >= COMMIT_BATCH_SIZE:
            df = pd.DataFrame.from_dict(self.commit_batch)
            df['timestamp'] = df['timestamp'].apply(pd.to_datetime)
            df.to_sql('domains', self.engine, if_exists='append', index=False)
            self.logger.info('wrote commit_batch to DB')
            res += COMMIT_BATCH_SIZE
            self.commit_batch.clear()
        return res

    def get_records(self, label=0, limit=1000, hosting=False, dash=True, columns=None):
        """[interface for the database]

        Keyword Arguments:
            label {[int]} -- [0 for benign, 1 for malicious] (default: {0})
            limit {int} -- [how many rows to return] (default: {1000})
            hosting {bool} -- [if to return hosting websites results] (default: {False})
            columns {[list]} -- [description] (default: {None})

        Returns:
            [df] {[DataFrame]} -- [returns None if an exception had occurred]
        """
        df = None
        try:
            select = f'SELECT {"*" if columns is None else ",".join(columns)}'
            where = f"WHERE label={label} {'' if hosting else HOSTING_QUERY}"
            dash = '' if dash else "AND domain_name NOT LIKE '%%-%%'"
            limit = f'LIMIT {limit}'
            SQL_QUERY = f'{select} FROM domains {where} {dash} {limit}'
            self.logger.info('running query: %s', SQL_QUERY)
            df = pd.read_sql_query(SQL_QUERY, self.engine)
        except Exception:
            self.logger.exception('error on query')
        return df
