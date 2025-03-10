import kfp
from kfp import dsl
from kfp import components
from kfp.components import func_to_container_op
from elasticsearch import Elasticsearch
import kubernetes.client

client = kfp.Client(host='IP address')

  
def metric_anomaly_detection(device: str) -> bool:
    from utils.result import Reporting
    reporting = Reporting(job='anomaly-detection')

    try:
        from metric_anomaly_main import metric_main
        metric_main(device)
    except Exception as e:
        reporting.report_result(result='fail', error=f'{device} Metric Anomaly Detection Error: {str(e)}')
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
    except Exception as e:
        reporting.report_result(result='fail', error=f'Log Anomaly Detection Error: {str(e)}')
        return False
    return True


def calc_total_score(a: bool, b: bool, c: bool):
    import sys
    sys.path.append('/anomaly/')
    from utils.result import Reporting
    reporting = Reporting(job='anomaly-detection')

    try:
        sys.path.append('/anomaly_detection')
        from calc_total_score_main import total_main
        total_main()
    except Exception as e:
        reporting.report_result(result='fail', error=f'Anomaly Score Calc Error: {str(e)}')
        return False
    reporting.report_result(result='success')
    return True


metric_anomaly_component = components.create_component_from_func(
    func=metric_anomaly_detection,
    base_image='aiops/base:latest'
)

log_anomaly_component = components.create_component_from_func(
    func=inference_log_anomaly,
    base_image='aiops/base:latest'
)

calc_total_score_component = components.create_component_from_func(
    func=calc_total_score,
    base_image='aiops/base:latest'
)


@dsl.pipeline(
    name="cantabile-calc-total-anomaly",
)
def calc_total_score_pl():
    # Define the image pull secret
    image_pull_secrets = [V1LocalObjectReference(name="aiops")]
    dsl.get_pipeline_conf().set_image_pull_secrets(image_pull_secrets)

    # Create tasks for metric anomaly detection (CPU and Memory)
    metric_task1 = metric_anomaly_component("cpu").add_pvolumes(
        {"/mnt/anomaly/": dsl.PipelineVolume(pvc='cantabile-pvc')})
    metric_task2 = metric_anomaly_component("memory").add_pvolumes(
        {"/mnt/anomaly/": dsl.PipelineVolume(pvc='cantabile-pvc')})

    # Create a task for log anomaly detection
    log_task = log_anomaly_component().add_pvolumes({"/mnt/anomaly/": dsl.PipelineVolume(pvc='cantabile-pvc')})

    # Create a task for calculating the total score
    total_score_task = calc_total_score_component(
        metric_task1.output,
        metric_task2.output,
        log_task.output
    ).add_pvolumes({"/mnt/anomaly/": dsl.PipelineVolume(pvc='cantabile-pvc')})


kfp.compiler.Compiler().compile(
    pipeline_func=calc_total_score_pl,
    package_path='total_anoamly_score_pl.yaml')

client.create_run_from_pipeline_func(calc_total_score_pl, arguments={})
