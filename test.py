print('start!')
import DataSource
from DataSource import OpenPhishDataSource, OPENPHISH_URL 
from DataSource import PhishTankDataSource, PHISHTANK_URL
from DataSource import AlexaDataSource, Alexa_URL
from FeatureExtraction import feature_extractor
print('Finished loading imports!')

openphish = OpenPhishDataSource(OPENPHISH_URL)
phishtank = PhishTankDataSource(PHISHTANK_URL)
alexa = AlexaDataSource(Alexa_URL)
print('Build data sources!')


for data_source in [alexa, openphish, phishtank]:
    url_list = data_source.fetch()
    print (len(url_list))
    df = feature_extractor.extract(url_list[:50], data_source.get_data_source_label())
    print (len(df))
    df.to_csv(f'{data_source.get_data_source_name()}.csv')