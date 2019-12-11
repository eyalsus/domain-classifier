class Model(object):
    def __init__(self):
        print('in Model const')
        
    def train(self, X, y=None):
        pass

    def predict(self, X):
        pass

    def __str__(self):
        return type(self).__name__
