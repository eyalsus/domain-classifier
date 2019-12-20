#!/bin/bash
sudo echo "Defining environment variables"
export PHISHTANK_APIKEY="d297d14ebc2b90cfbca8e0b1d041c4dc692e0a4454818659e629a0352048a10e"
export LOG_DIR_PATH="/home/eyalp/logs"
export ASN_DB_PATH="/home/eyalp/domain-classifier/resources"
export FETCH_SLEEP_TIME=3600
sudo service redis-server restart
sudo service postgresql restart
echo "Restart postgresql and redis done."
sleep 10
nohup python3 /home/eyalp/domain-classifier/enrich_domain.py --debug-level INFO &
echo "Start to train models"
python3 model_manager.py --pkl-path 10K10K.pkl --limit 10000 --train
nohup python3 model_manager.py --pkl-path 10K10K.pkl --listen --retrain 2 --limit 10000 &
echo "Done trianing, listening for new domains"
echo "Fetching malicious domains"
nohup python3 /home/eyalp/domain-classifier/fetch_feeds.py --data-source PhishTank --infinity --sleep 3600 &
nohup python3 /home/eyalp/domain-classifier/fetch_feeds.py --data-source OpenPhish --infinity --sleep 3600 &
sleep 60
echo "Fetching benign domains"
nohup python3 /home/eyalp/domain-classifier/fetch_feeds.py --data-source Alexa --infinity --sleep 86400 --limit 50000 &
nohup python3 /home/eyalp/domain-classifier/fetch_feeds.py --data-source OpenDNS --infinity --sleep 86400 --limit 50000 &
sleep 10
echo "Done."