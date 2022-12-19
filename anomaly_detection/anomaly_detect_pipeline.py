import kfp
from kfp import dsl
from kfp import components
from kfp.components import func_to_container_op
from elasticsearch import Elasticsearch
import kubernetes.client
client = kfp.Client(host='IP address')

def metric_anomaly_detection(device: str) -> bool:
    import sys
    sys.path.append('/anomaly/')
    from utils.result import Reporting
    reporting = Reporting(job='anomaly-detection')

    try:
        sys.path.append('/anomaly_detection')
        from metric_anomaly_main import metric_main
        metric_main(device)
    except:
        reporting.report_result(result='fail', error=f'{device} Metric Anomaly Detection Error')
        return False
    
    return True

def inference_log_anomaly() -> bool:
    import sys
    sys.path.append('/anomaly/')
    from utils.result import Reporting
    reporting = Reporting(job='croffle-anomaly-detection')

    try:
        sys.path.append('/anomaly_detection')
        from log_anomaly_inference import Log_Anomaly_Inference
        config_path = '/anomaly_detection/config.ini'
        save_path = "/log_anomaly"
        train = Log_Anomaly_Inference(config_path, save_path)
        train.run()
    except:
        reporting.report_result(result='fail', error=f'Log Anomaly Detection Error')
        return False
    return True