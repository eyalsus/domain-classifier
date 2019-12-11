import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from Model.Model import Model


class MLModel(Model):
    feature_dummies = ['ns_base_domain', 'ns_as_subnet', 'ns_as_name']
    def __init__(self, clf=None):
        self.features = None
        if clf:
            self.clf = clf
        else:
            self.clf = DecisionTreeClassifier()

    def train(self, X, y=None):
        X = pd.get_dummies(X[MLModel.feature_dummies])
        self.features = list(X.columns)
        print(f'train - features extracted: {len(self.features)}')
        self.clf.fit(X, y)
        # score = self.clf.score(X_test, y_test)
        # print (f'{name}: {score}')

    def predict(self, X):
        X = pd.get_dummies(X[MLModel.feature_dummies])
        print(f'predict #1 - features extracted: {len(X.columns)}')
        zeros_df = pd.DataFrame(0, index=X.index, columns=self.features)
        # zeros_df = X * 0
        X = X.add(zeros_df, fill_value=0)
        X = X[X.columns & self.features]
        print(f'predict #2 - features extracted: {len(X.columns)}')
        return self.clf.predict_proba(X[self.features])

    def __str__(self):
        return f'{type(self).__name__}_{type(self.clf).__name__}'
