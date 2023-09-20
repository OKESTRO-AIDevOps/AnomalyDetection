import os
import sys
import configparser
from elasticsearch import Elasticsearch
from total_anomaly import TotalAnomaly
from elasticsearch import ElasticsearchDeprecationWarning
import warnings
warnings.filterwarnings(action='ignore', category=ElasticsearchDeprecationWarning)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))))
from utils.logs.log import standardLog
standardLog = standardLog()

def connect_to_elasticsearch():
    config = configparser.ConfigParser()
    config.read('/croffle/config.ini')

    es_host = config.get('ES', 'HOST')
    es_port = config.get('ES', 'PORT')
    es_id = config.get('ES', 'USER')
    es_pw = config.get('ES', 'PASSWORD')

    try:
        es = Elasticsearch(hosts=f"http://{es_id}:{es_pw}@{es_host}:{es_port}/", timeout=1000)
        return es
    except Exception as e:
        log_error_and_exit("AnomalyDetection Connect ES error", e)

def log_error_and_exit(message, error=None):
    standardLog.sending_log('error', error).error(message)
    exit(1)

def main():
    try:
        es = connect_to_elasticsearch()
        total_anomaly = TotalAnomaly(es)
        total_anomaly.retrieve_metric_anomaly()
        total_anomaly.retrieve_log_anomaly()
        total_anomaly.update_total_anomaly_score()
        standardLog.sending_log('success').info('AnomalyDetection calc total score success')
    except Exception as e:
        log_error_and_exit(f'AnomalyDetection total error', e)

if __name__ == "__main__":
    main()