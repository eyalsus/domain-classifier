import dns.resolver
import tldextract
import pyasn
from netaddr import IPNetwork
from pyasn_util_asnames import download_asnames, _html_to_dict
import pandas as pd
from common import get_domain_from_url, get_base_domain, read_file
from datetime import datetime
import os
class _FeatureExtraction(object):

    
    def  __init__(self):
        asn_path = os.getenv('ASN_DB_PATH')
        self.asndb = pyasn.pyasn(os.path.join(asn_path, 'asn20190719.db'))
        data = download_asnames()
        self.asn_dict = _html_to_dict(data)


    def extract_domain_features(self, domain, label):
        features = {'domain': domain, 'label': label}
        features['timestamp'] = datetime.now().isoformat()
        
        base_domain = get_base_domain(domain)
        # domain features
        features['base_domain'] = base_domain
        features['domain_name'] = self.__get_domain_name(domain)
        features['domain_ip'] = self.__get_domain_ip(domain)

        # AS features
        as_number, as_subnet = self.__get_ASN_and_subnet_by_IP(features['domain_ip'])
        features['as_number'] = as_number
        features['as_subnet'] = as_subnet
        features['as_name'] = self.__get_as_name(as_number)

        # name server features
        nameserver = self.__get_domain_name_server(base_domain)
        features['nameserver'] = nameserver
        features['ns_base_domain'] = get_base_domain(nameserver)
        features['ns_domain_ip'] = self.__get_domain_ip(nameserver)
        ns_as_number, ns_as_subnet = self.__get_ASN_and_subnet_by_IP(features['ns_domain_ip'])
        features['ns_as_number'] = ns_as_number
        features['ns_as_subnet'] = ns_as_subnet
        features['ns_as_name'] = self.__get_as_name(ns_as_number)
        
        return features


    def extract(self, df):        
        df.loc[:, 'domain_name'] = df['domain'].apply(self.__get_domain_name)
        df.loc[:, 'base_domain'] = df['domain'].apply(get_base_domain)
        # df.loc[:, 'trigrams'] = df['domain_name'].apply(self.__extract_trigrams)
        df.loc[:, 'domain_ip'] = df['domain'].apply(self.__get_domain_ip)

        df.loc[:, 'as_subnet'] = df['domain_ip'].apply(self.__get_ASN_and_subnet_by_IP)
        df.loc[:, 'as_number'] = df['as_subnet'].apply(lambda x: x[0])
        df.loc[:, 'as_subnet'] = df['as_subnet'].apply(lambda x: x[1])
        df.loc[:, 'as_name'] = df['as_number'].apply(self.__get_as_name)

        # name server features
        df.loc[:, 'name_server'] = df['base_domain'].apply(self.__get_domain_name_server)
        df.loc[:, 'ns_base_domain'] = df['name_server'].apply(get_base_domain)
        df.loc[:, 'ns_ip'] = df['name_server'].apply(self.__get_domain_ip)
        df.loc[:, 'ns_as_subnet'] = df['ns_ip'].apply(self.__get_ASN_and_subnet_by_IP)
        df.loc[:, 'ns_as_number'] = df['ns_as_subnet'].apply(lambda x: x[0])
        df.loc[:, 'ns_as_subnet'] = df['ns_as_subnet'].apply(lambda x: x[1])
        df.loc[:, 'ns_as_name'] = df['ns_as_number'].apply(self.__get_as_name)

        df.set_index('domain', inplace=True)
        
        return df

    def _extract_previous(self, url_list, origin, label):
        df = pd.DataFrame(url_list, columns=['url'])
        df.loc[:, 'domain'] = df['url'].apply(get_domain_from_url)
        df.drop_duplicates(subset=df.columns.difference(['url']), inplace=True)
        
        df.loc[:, 'domain_name'] = df['domain'].apply(self.__get_domain_name)
        df.loc[:, 'base_domain'] = df['domain'].apply(get_base_domain)
        # df.loc[:, 'trigrams'] = df['domain_name'].apply(self.__extract_trigrams)
        df.loc[:, 'domain_ip'] = df['domain'].apply(self.__get_domain_ip)

        df.loc[:, 'as_subnet'] = df['domain_ip'].apply(self.__get_ASN_and_subnet_by_IP)
        df.loc[:, 'as_number'] = df['as_subnet'].apply(lambda x: x[0])
        df.loc[:, 'as_subnet'] = df['as_subnet'].apply(lambda x: x[1])
        df.loc[:, 'as_name'] = df['as_number'].apply(self.__get_as_name)

        # name server features
        df.loc[:, 'name_server'] = df['base_domain'].apply(self.__get_domain_name_server)
        df.loc[:, 'ns_base_domain'] = df['name_server'].apply(get_base_domain)
        df.loc[:, 'ns_ip'] = df['name_server'].apply(self.__get_domain_ip)
        df.loc[:, 'ns_as_subnet'] = df['ns_ip'].apply(self.__get_ASN_and_subnet_by_IP)
        df.loc[:, 'ns_as_number'] = df['ns_as_subnet'].apply(lambda x: x[0])
        df.loc[:, 'ns_as_subnet'] = df['ns_as_subnet'].apply(lambda x: x[1])
        df.loc[:, 'ns_as_name'] = df['ns_as_number'].apply(self.__get_as_name)
        df.loc[:, 'origin'] = origin
        df.loc[:, 'label'] = label

        df.set_index('domain', inplace=True)
        
        return df

    def __extract_trigrams(self, domain_name):
        trigrams = set()
        for i in range(0, len(domain_name) - 2):
            trigrams.add(domain_name[i:i+3])
        return trigrams


    def __get_domain_ip(self, domain):
        ip = None
        try:
            res = dns.resolver.query(domain, 'A')
            ip = res[0].address
        except:
            print (f'{domain} - NX domain')
        return ip


    def __get_domain_name_server(self, domain):
        ns = None
        try:
            res = dns.resolver.query(domain, 'NS')
            ns = res[0].to_text()[:-1]
        except:
            print (f'{domain} - NX domain')
        return ns


    # def __get_domain_from_url(self, url):
    #     domain = None
    #     try:
    #         exr = tldextract.extract(url)
    #         if exr.subdomain:
    #             domain = f'{exr.subdomain}.{exr.domain}.{exr.suffix}'
    #         else:
    #             domain = f'{exr.domain}.{exr.suffix}'
    #     except:
    #         print (f'error get domain of {url}')
    #     return domain


    # def __get_base_domain(self, domain):
    #     base_domain = None
    #     try:
    #         exr = tldextract.extract(domain)
    #         base_domain = f'{exr.domain}.{exr.suffix}'
    #     except:
    #         print (f'error get base domain of {domain}')
    #     return base_domain


    def __get_domain_name(self, domain):
        domain_name = None
        try:
            exr = tldextract.extract(domain)
            domain_name = exr.domain
        except:
            print (f'error get domain name of {domain}')
        return domain_name


    def __get_ASN_and_subnet_by_IP(self, ip):
        as_number = None
        subnet = None
        if ip:
            try:
                asn, subnet = self.asndb.lookup(ip)
                as_number = str(asn)
            except:
                print(f'cannot resolve ASN for ip: {ip}')
        return as_number, subnet


    def __get_network_address(self, ip, mask=16):
        network = None
        try:
            network = str(IPNetwork(f'{ip}/{mask}').cidr)
        except:
            print(f'cannot resolve network for ip: {ip}')
        return network


    def __get_as_name(self, as_number):
        as_name = None
        if as_number and as_number in self.asn_dict:
            as_name = self.asn_dict[as_number]
        return as_name


feature_extractor =  _FeatureExtraction()
