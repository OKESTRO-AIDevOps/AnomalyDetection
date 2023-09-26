import os
import sys
import configparser
from elasticsearch import Elasticsearch, ElasticsearchDeprecationWarning
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress Elasticsearch deprecation warnings
import warnings
warnings.filterwarnings(action='ignore', category=ElasticsearchDeprecationWarning)

def load_config():
    config = configparser.ConfigParser()
    abs_path = '/croffle'  # Change this to your desired absolute path
    config_file = os.path.join(abs_path, "config.ini")
    config.read(config_file)
    return config

def connect_to_elasticsearch(config):
    es_host = config.get('ES', 'HOST')
    es_port = config.get('ES', 'PORT')
    es_id = config.get('ES', 'USER')
    es_pw = config.get('ES', 'PASSWORD')  # You need to add this line for password

    try:
        es = Elasticsearch(hosts=f"http://{es_id}:{es_pw}@{es_host}:{es_port}/", timeout=1000)
        return es
    except Exception as e:
        logger.error('AnomalyDetection Connect ES error: %s', e)
        sys.exit(1)

def main(device):
    config = load_config()

    try:
        es = connect_to_elasticsearch(config)
    except Exception as e:
        logger.error('AnomalyDetection Connect ES error: %s', e)
        sys.exit(1)

    try:
        metric_anomaly = MetricAnomaly(es, device)
    except Exception as e:
        logger.error(f'AnomalyDetection {device} metric init error: %s', e)
        sys.exit(1)

    try:
        metric_anomaly.calculate_predict_std()
    except Exception as e:
        logger.error(f'AnomalyDetection {device} calc std error: %s', e)
        sys.exit(1)

    try:
        metric_anomaly.calculate_metric_anomaly()
    except Exception as e:
        logger.error(f'AnomalyDetection {device} calc score error: %s', e)
        sys.exit(1)

    try:
        metric_anomaly.write_metric_anomaly_to_es()
    except Exception as e:
        logger.error(f'AnomalyDetection {device} es write error: %s', e)
        sys.exit(1)

    logger.info('AnomalyDetection %s metric calc success', device)

if __name__ == "__main__":
    device_name = "your_device_name_here"  # Replace with the actual device name
    main(device_name)