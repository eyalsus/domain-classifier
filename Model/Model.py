import logging
import sys
import pickle
from datetime import datetime


class Model(object):
    def __init__(self, logger=None):
        self.set_logger(logger)
        self.train_date = datetime.now()
        self.logger.debug('in Model __init__')

    def save_model(self, pkl_path):
        tmp = self.logger
        delattr(self, 'logger')
        with open(pkl_path, 'wb') as pkl_file:
            pickle.dump(self, pkl_file)
        self.logger = tmp

    @classmethod
    def load_model(cls, pkl_path, logger=None):
        with open(pkl_path, 'rb') as f:
            model = pickle.load(f)
            model.set_logger(logger)
            if hasattr(model, 'model_list'):
                for model_component in model.model_list:
                    model_component.set_logger(logger)
        return model

    def train(self, X, y=None):
        self.train_date = datetime.now()

    def predict(self, X):
        pass

    def set_logger(self, logger):
        if logger:
            self.logger = logger
        else:
            logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
            self.logger = logging

    def __str__(self):
        return type(self).__name__
