#!/bin/bash
sudo echo "Defining environment variables"
export PHISHTANK_APIKEY=""
export LOG_DIR_PATH="/home/eyalp/logs"
export ASN_DB_PATH="/home/eyalp/domain-classifier/resources"
sudo service redis-server restart
sudo service postgresql restart
echo "Restart postgresql and redis done."
sleep 1
nohup python3 /home/eyalp/domain-classifier/enrich_domain.py --postgresql-username postgres --postgresql-password mypassword --debug-level DEBUG &
echo "Start to train models"
python3 model_manager.py --pkl-path 10K10K.pkl --limit 10000 --train --postgresql-username postgres --postgresql-password mypassword
echo "Done trianing, listening for new domains"
nohup python3 model_manager.py --pkl-path 10K10K.pkl --listen --retrain 4 --limit 10000 --postgresql-username postgres --postgresql-password mypassword --debug-level DEBUG &
echo "Fetching malicious domains"
nohup python3 /home/eyalp/domain-classifier/fetch_feeds.py --data-source PhishTank --infinity --sleep 3600 --debug-level INFO &
nohup python3 /home/eyalp/domain-classifier/fetch_feeds.py --data-source OpenPhish --infinity --sleep 3600 --debug-level INFO &
sleep 60
echo "Fetching benign domains"
nohup python3 /home/eyalp/domain-classifier/fetch_feeds.py --data-source Alexa --infinity --sleep 86400 --limit 50000 --debug-level INFO &
nohup python3 /home/eyalp/domain-classifier/fetch_feeds.py --data-source OpenDNS --infinity --sleep 86400 --limit 50000 --debug-level INFO &
sleep 10
echo "Done."
