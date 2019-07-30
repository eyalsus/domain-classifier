import DataSource
from DataSource import OpenPhishDataSource, OPENPHISH_URL, PhishTankDataSource, PHISHTANK_URL
from FeatureExtraction import feature_extractor

openphish = OpenPhishDataSource(OPENPHISH_URL)
phishtank = PhishTankDataSource(PHISHTANK_URL)



for data_source in [openphish, phishtank]:
    url_list = data_source.fetch()
    print (len(url_list))
    df = feature_extractor.extract(url_list[:50], 1)
    print (len(df))
    df.to_csv(f'{data_source.get_data_source_name()}.csv')