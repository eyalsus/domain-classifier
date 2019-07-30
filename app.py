from main import handle_domain_list
from flask import request
from flask import Flask
import json

app = Flask(__name__)

@app.route('/', methods=['POST'])
def handle_domain_request():
    d = request.get_json()
    if d and 'domain_list' in d and 'label' in d:
            features_df = handle_domain_list(d['domain_list'], d['label'])
    return features_df.T.to_json()


if __name__ == '__main__':
    app.run(debug=True)