from flask import Flask, render_template, request, Markup, redirect
import pandas as pd
import argparse
from DatabaseConnector import DatabaseConnector
from Model.AggragatorModel import AggragatorModel
from FeatureExtraction import feature_extractor
from common import get_domain_from_url

app = Flask(__name__)

EXPLORE_PAGE = 50
db_conn = None
agg_model = None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--flask-host", type=str, default='localhost', help="flask host")
    parser.add_argument("--flask-port", type=int, default=8080, help="flask port")
    parser.add_argument("--logger", type=str, default='webapp', help='logger name')
    parser.add_argument("--pkl-path", type=str, default='10K10K.pkl', help='path to pickle to save/load the model file')
    parser.add_argument("--limit", type=int, default=1000, help='limit records per classification')
    parser.add_argument("--postgresql-host", type=str, default='localhost', help="postgresql host")
    parser.add_argument("--postgresql-port", type=int, default=5432, help="postgresql port")
    parser.add_argument("--postgresql-username", type=str, help="postgresql username")
    parser.add_argument("--postgresql-password", type=str, help="postgresql password")
    parser.add_argument("--debug-level", type=str, default='INFO', help='logging debug level')
    args = parser.parse_args()
    
    global db_conn, agg_model
    agg_model = AggragatorModel.load_model(args.pkl_path)
    db_conn = DatabaseConnector(
        args.postgresql_username,
        args.postgresql_password,
        args.postgresql_host,
        args.postgresql_port
    )
    app.run(host=args.flask_host, port=args.flask_port)

@app.route('/', methods=['GET'])
def home():
    return redirect("/domain-reputation", code=302)

@app.route('/explore-dataset', methods=['GET'])
def explore_dataset():
    start = request.args.get('start')
    if not start:
        start = 0
    else:
        start = int(start)
    X = db_conn.get_all_records(limit=1000)
    return render_template(
        'Explore-Dataset.html',
        X=Markup(X[start:start + 50].to_html()),
        prev_path=f'/explore-dataset?start={0 if start == 0 else start + 50}',
        next_path=f'/explore-dataset?start={start + 50}'
    )

@app.route('/domain-reputation', methods=['GET', 'POST'])
def domain_reputation():
    url = request.form.get('url')
    domain = get_domain_from_url(url)
    print(url)
    if domain:
        fv_dict = feature_extractor.extract_domain_features(domain)
        X = pd.DataFrame.from_dict([fv_dict])
        y_pred = agg_model.predict(X)
        print('domain: {domain}')
        print(y_pred)
        return render_template(
            'Domain-Reputation.html',
            url=url,
            y_pred=Markup(y_pred.to_html(index=False)),
            X=Markup(X.T.to_html(header=False)),
            )
    return render_template('Domain-Reputation.html', domain='', X='')

if __name__ == '__main__':
    main()