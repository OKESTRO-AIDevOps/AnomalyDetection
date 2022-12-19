import kfp
from kfp import dsl
from kfp import components
from kfp.components import func_to_container_op
import kubernetes.client
client = kfp.Client(host='IP address')


def train_log_anomaly():
    import sys
    sys.path.append('/anomaly_detection')
    from log_anomaly_train import Log_Anomaly_Model

    sys.path.append('/croffle/')
    from utils.result import Reporting
    reporting = Reporting(job='anomaly-detection')

    config_path = '/anomaly_detection/config.ini'
    save_path = "/log_anomaly"
    try:
        train = Log_Anomaly_Model(config_path, save_path)
        train.run()
    except:
        reporting.report_result(result='fail', error=f'Train Log Anomaly Error')
        exit(1)
    reporting.report_result(result='success')

@dsl.pipeline(
    name="train-log-anomaly",
)
def train_log_anomaly_pl():
    dsl.get_pipeline_conf().set_image_pull_secrets([kubernetes.client.V1LocalObjectReference(name="aiops")])
    op = dsl.PipelineVolume(pvc='cantabile-pvc')
    searching = components.create_component_from_func(
        func=train_log_anomaly,                       
        base_image='aiops/base:latest'
    )
    searching().set_memory_limit("10Gi").add_pvolumes({"/mnt/symphony/": op})

kfp.compiler.Compiler().compile(
    pipeline_func=train_log_anomaly_pl,
    package_path='train_log_anomaly_pl.yaml')


client.create_run_from_pipeline_func(train_log_anomaly_pl, arguments={})
# client.create_recurring_run(
#     experiment_id = client.get_experiment(experiment_name="Default").id,
#     job_name="train-log-anomaly",
#     description="version: croffle:feature/pipeline-migration",
#     cron_expression="0 0 19 * *",
#     pipeline_package_path = "./train_log_anomaly_pl.yaml")