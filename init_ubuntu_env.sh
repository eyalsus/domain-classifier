
export PHISHTANK_APIKEY="d297d14ebc2b90cfbca8e0b1d041c4dc692e0a4454818659e629a0352048a10e"
sudo service redis-server start
sudo service postgresql start
nohup python3 /home/eyalp/domain-classifier/enrich_domain.py &> /home/eyalp/enrich_domain.log &
nohup python3 /home/eyalp/domain-classifier/database_connector.py &> /home/eyalp/database_connector.log &
sudo service cron start