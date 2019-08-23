import tldextract
from datetime import timedelta
import cloudstorage as gcs
import re

IP_REGEX = re.compile(r'\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}')

def get_domain_from_url(url):
    domain = None
    try:
        exr = tldextract.extract(url)
        if exr.subdomain:
            domain = f'{exr.subdomain}.{exr.domain}.{exr.suffix}'
        else:
            domain = f'{exr.domain}.{exr.suffix}'

        if IP_REGEX.match(domain):
            domain = None
    except:
        print (f'error get domain of {url}')
    return domain


def get_base_domain(domain):
    base_domain = None
    try:
        exr = tldextract.extract(domain)
        base_domain = f'{exr.domain}.{exr.suffix}'
    except:
        print (f'error get base domain of {domain}')
    return base_domain


def round_time(dt, roundTo=60):
   """Round a datetime object to any time lapse in seconds
   dt : datetime.datetime object, default now.
   roundTo : Closest number of seconds to round to, default 1 minute.
   Author: Thierry Husson 2012 - Use it as you want but don't blame me.
   """
   seconds = (dt.replace(tzinfo=None) - dt.min).seconds
   rounding = (seconds+roundTo/2) // roundTo * roundTo
   return dt + timedelta(0, rounding-seconds, -dt.microsecond)


def read_file(filename):
    gcs_file = gcs.open(filename)
    contents = gcs_file.read()
    gcs_file.close()
    return contents