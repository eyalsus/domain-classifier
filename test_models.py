import pandas as pd 
from sklearn.model_selection import train_test_split
from sqlalchemy import create_engine
from Model.MarkovModel import MarkovModel
from Model.SnaModel import SnaModel
from Model.MLModel import MLModel
from Model.AggragatorModel import AggragatorModel

MALICIOUS_QUERY_STR = f''' 
SELECT * 
FROM domains 
WHERE label = 1
AND base_domain NOT IN ('000webhostapp.com', 'azurewebsites.net') 
AND domain_name NOT LIKE '%%-%%' 
order by timestamp desc
LIMIT {1000} 
'''  

BENIGN_QUERY_STR = f''' 
SELECT * 
FROM domains 
WHERE label = 0
AND domain_name NOT LIKE '%%-%%' 
order by timestamp desc
LIMIT {1000} 
'''  

engine = create_engine('postgresql://postgres:mypassword@localhost:5432/')
X_malicious = pd.read_sql_query(MALICIOUS_QUERY_STR, engine)
X_benign = pd.read_sql_query(BENIGN_QUERY_STR, engine)
X = pd.concat([X_malicious, X_benign])
print(f'X_malicious: {len(X_malicious)}, X_benign: {len(X_benign)}, X: {len(X)}')

y = X['label']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

ml_model = MLModel()
sna_model = SnaModel()
markov_model = MarkovModel()
model_list = [markov_model, sna_model, ml_model]
agg_model = AggragatorModel(model_list)
agg_model.train(X_train, y_train)
predict_df = agg_model.predict(X_test)

# print(f'First X_test Ten:\n{X_test.head(10)}')
# for model in [ml_model, sna_model]:
#     model.train(X_train, y_train)
#     print(f'{model} Predict First X_benign Ten\n{model.predict(X_benign[:10])}')
#     print(f'{model} Predict First X_malicious Ten\n{model.predict(X_malicious[:10])}')
#     print(f'{model} Predict First X_test Ten\n{model.predict(X_test[:10])}')
    
# #print(f'last X_test Ten:\n{X_test.tail(10)}')

# markov_model = MarkovModel()
# markov_model.train(X_malicious)

# print(f'markov model prediction of benign domains:\n{markov_model.predict(X_benign[:10])}')

# i = 0
# true_dict = []
# for item in markov_model.domain_name_set:
#     if i >= 5:
# 	    break
#     true_dict.append({'domain_name': item})
#     i += 1
# print(f'markov model self test:\n{markov_model.predict(pd.DataFrame.from_dict(true_dict))}')

