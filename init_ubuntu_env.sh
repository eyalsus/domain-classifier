
#!/bin/bash
sudo echo "Running domain classifier in background..."
export PHISHTANK_APIKEY="d297d14ebc2b90cfbca8e0b1d041c4dc692e0a4454818659e629a0352048a10e"
export LOG_DIR_PATH="/home/eyalp/logs"
export ASN_DB_PATH="/home/eyalp/domain-classifier/resources"
export FETCH_SLEEP_TIME=3600
sudo service redis-server restart
sudo service postgresql restart
nohup python3 /home/eyalp/domain-classifier/enrich_domain.py &
sleep 5
nohup python3 /home/eyalp/domain-classifier/database_connector.py &
sleep 5
nohup python3 /home/eyalp/domain-classifier/fetch_feeds.py --data-source PhishTank --infinity &
sleep 5
nohup python3 /home/eyalp/domain-classifier/fetch_feeds.py --data-source OpenPhish --infinity &
#sudo service cron start