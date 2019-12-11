from Model.Model import Model


class AggragatorModel(Model):
    def __init__(self, model_list):
        self.model_list = model_list

    def train(self, X, y=None):
        for model in self.model_list:
            model.train(X, y)

    def predict(self, X=None):
        df = pd.DataFrame()
        for model in self.model_list:
            model.fit(X, y)