gcloud functions deploy domains_feature_extraction_pubsub --runtime python37 --trigger-topic=enrich-domains --env-vars-file env.yaml