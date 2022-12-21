# -- coding: utf-8 --
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

def total_main():
    # configparser
    config = configparser.ConfigParser()
    abs_path = '/croffle'
    config.read(abs_path + "/config.ini")

    # es config
    es_host=config.get('ES','HOST')
    es_port=config.get('ES','PORT')
    es_id=config.get('ES','USER')
    es_pw=config.get('ES','PASSWORD')

    # es read
    try:
        es = Elasticsearch(hosts=f"http://{es_id}:{es_pw}@{es_host}:{es_port}/", timeout=1000)
    except Exception as e:
        standardLog.sending_log('error', e).error('AnomalyDetection Connect ES error')
        exit(1)