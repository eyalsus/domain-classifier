from time import time
import pandas as pd
from Model.Model import Model

DUMMY_FEATURE_LIST = ['ns_base_domain', 'ns_as_subnet', 'ns_as_name']

class MLModel(Model):
    def __init__(self, clf, logger=None):
        super().__init__(logger)
        self.features_list = []
        self.features_set = set()
        self._clf = clf

    def train(self, X, y=None):
        super().train(X, y)
        X = pd.get_dummies(X[DUMMY_FEATURE_LIST])
        self.features_list = list(X.columns)
        self.features_set = set(X.columns)
        self.logger.debug(f'train - features extracted: {len(self.features_list)}')
        self._clf.fit(X, y)
        # score = self.clf.score(X_test, y_test)
        # print (f'{name}: {score}')

    def predict(self, X):
        start = time()
        X = pd.get_dummies(X[MLModel.feature_dummies])
        dummies_time = time()
        self.logger.debug(f'get_dummies duration: {dummies_time - start}')
        zeros_df = pd.DataFrame(0, index=X.index, columns=self.features_list)
        zeros_time = time()
        self.logger.debug(f'zeros_time duration: {zeros_time - dummies_time}')
        drop_column_list = set(X.columns) - self.features_set
        if len(drop_column_list) > 0:
            X.drop(columns=drop_column_list, inplace=True)
        X = X.add(zeros_df)
        X.fillna(0, inplace=True)
        # REPLACE X = X.add(zeros_df, fill_value=0)
        add_time = time()
        self.logger.debug(f'add duration: {add_time - zeros_time}')
        # X = X[X.columns & self.features]
        filter_time = time()
        self.logger.debug(f'filter duration: {filter_time - add_time}')
        self.logger.debug(f'len(self.features): {len(self.features_list)}')
        self.logger.debug(f'len(X.columns): {len(X.columns)}')
        y_pred = self._clf.predict_proba(X[self.features_list]).transpose()[1]
        predict_time = time()
        self.logger.debug(f'predict duration: {predict_time - filter_time}')
        return y_pred

    def __str__(self):
        return f'{type(self).__name__}_{type(self.__clf).__name__}'
