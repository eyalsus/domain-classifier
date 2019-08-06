from main import collect_data
from flask import request
from flask import Flask
import json

app = Flask(__name__)

@app.route('/collect', methods=['POST'])
def collect_data_flask():
    data_source_limit = 500
    d = request.get_json()
    if 'limit' in d:
        data_source_limit = d['limit']
    print (f'data_source_limit: {data_source_limit}')
    json_data = collect_data(data_source_limit)
    return json_data


if __name__ == '__main__':
    app.run(debug=True)