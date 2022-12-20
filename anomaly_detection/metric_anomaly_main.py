import os
import sys
import warnings
import configparser
from elasticsearch import Elasticsearch
from elasticsearch import ElasticsearchDeprecationWarning
from metric_anomaly import MetricAnomaly
warnings.filterwarnings(action='ignore', category=ElasticsearchDeprecationWarning)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))))

from utils.logs.log import standardLog
standardLog = standardLog()

def metric_main(device):
    config = configparser.ConfigParser()
    abs_path = '/croffle'
    config.read(abs_path + "/config.ini")
    es_host=config.get('ES','HOST')
    es_port=config.get('ES','PORT')
    es_id=config.get('ES','USER')
    try:
        es = Elasticsearch(hosts=f"http://{es_id}:{es_pw}@{es_host}:{es_port}/", timeout=1000)
    except Exception as e:
        standardLog.sending_log('error', e).error('AnomalyDetection Connect ES error')
        exit(1)

    try:
        metric_anomaly = MetricAnomaly(es, device)
    except Exception as e:
        standardLog.sending_log('error', e).error(f'AnomalyDetection {device} metric init error')
        exit(1)

    try:
        metric_anomaly.calculate_predict_std()
    except Exception as e:
        standardLog.sending_log('error', e).error(f'AnomalyDetection {device} calc std error')
        exit(1)

    try:
        metric_anomaly.calculate_metric_anomaly()
    except Exception as e:
        standardLog.sending_log('error', e).error(f'AnomalyDetection {device} calc score error')
        exit(1)

    try:
        metric_anomaly.write_metric_anomaly_to_es()
    except Exception as e:
        standardLog.sending_log('error', e).error(f'AnomalyDetection {device} es write error')
        exit(1)

    standardLog.sending_log('success').info('AnomalyDetection {device} metric calc success')

