from time import time
import pandas as pd
from Model.Model import Model
from Model.MarkovModel import MarkovModel


class AggragatorModel(Model):
    def __init__(self, model_list, logger=None):
        super().__init__(logger)
        self.model_list = model_list

    def save_model(self, pkl_path):
        tmp_logger_list = []
        for model in self.model_list:
            tmp_logger_list.append(model.logger)
            delattr(model, 'logger')
        super().save_model(pkl_path)
        
        i = 0
        for model in self.model_list:
            model.logger = tmp_logger_list[i]
            i += 1

    def train(self, X, y=None):
        super().train(X, y)
        for model in self.model_list:
            self.logger.debug(f'train {model}')
            if isinstance(model, MarkovModel):
                model.train(X[(X['label'] == 1) & ~(X['domain_name'].str.contains('-'))])
            else:
                model.train(X, y)

    def predict(self, X=None):
        df = pd.DataFrame(0, index=X.index, columns=[])
        for model in self.model_list:
            self.logger.debug(f'predict {model}')
            start = time()
            df[str(model).lower()] = model.predict(X)
            end = time()
            self.logger.debug(f'{model} took {round(end - start, 2)} sec')
        df['train_date'] = self.train_date.isoformat()
        return df

