sudo echo "Hello"
export PHISHTANK_APIKEY="d297d14ebc2b90cfbca8e0b1d041c4dc692e0a4454818659e629a0352048a10e"
export LOG_DIR_PATH="/home/eyalp/logs"
export ASN_DB_PATH="/home/eyalp/domain-classifier/resources"
export FETCH_SLEEP_TIME=3600
sudo service redis-server start
sudo service postgresql start
nohup python3 /home/eyalp/domain-classifier/enrich_domain.py &
nohup python3 /home/eyalp/domain-classifier/database_connector.py &
nohup python3 /home/eyalp/domain-classifier/fetch_feeds.py --data-source PhishTank --infinity &
nohup python3 /home/eyalp/domain-classifier/fetch_feeds.py --data-source OpenPhish --infinity &
#sudo service cron start