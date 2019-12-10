import pandas as pd
from Model.Model import Model


class MLModel(object):
    def __init__(self):
        print('in MLModel const')

    def train(self, X, y=None):
        X_dummies = pd.get_dummies(X[['ns_base_domain', 'ns_as_subnet', 'ns_as_name']].drop(columns='label'))

    def predict(self, X):
        pass
