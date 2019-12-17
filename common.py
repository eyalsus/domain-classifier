import tldextract
from datetime import timedelta, datetime
import re
import logging
import os

IP_REGEX = re.compile(r'\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}')
debug_level_dict = {
    'CRITICAL': logging.CRITICAL,
    'FATAL': logging.FATAL,
    'ERROR': logging.ERROR,
    'WARNING': logging.WARNING,
    'WARN': logging.WARN,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
    'NOTSET': logging.NOTSET
}

def define_logger(logger_name, debug_level='INFO'):
    logger = logging.getLogger(logger_name)
    if debug_level in debug_level_dict:
        logger.setLevel(debug_level_dict[debug_level])
    log_dir_path = os.getenv('LOG_DIR_PATH')
    if log_dir_path is None:
        log_dir_path = '/home/eyalp/logs'
    date_str = datetime.now().isoformat().replace(':', '_').split('.')[0]
    log_file_name = f'{logger_name}_{date_str}.log'
    log_file_path = os.path.join(log_dir_path, log_file_name)
    fh = logging.FileHandler(log_file_path)
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger

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
    except Exception:
        print(f'error get domain of {url}')
    return domain


def get_base_domain(domain):
    base_domain = None
    try:
        exr = tldextract.extract(domain)
        base_domain = f'{exr.domain}.{exr.suffix}'
    except Exception:
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


# def read_file(filename):
#     gcs_file = gcs.open(filename)
#     contents = gcs_file.read()
#     gcs_file.close()
#     return contents