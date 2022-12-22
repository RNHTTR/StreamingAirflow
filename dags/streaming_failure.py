from datetime import datetime, timedelta
from airflow import DAG, Dataset
from airflow.configuration import conf
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator
from astronomer.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperatorAsync


namespace = conf.get('kubernetes', 'NAMESPACE')
# This will detect the default namespace locally and read the
# environment namespace when deployed to Astronomer.
if namespace =='default':
    config_file = '/usr/local/airflow/include/.kube/config'
    in_cluster = False
else:
    in_cluster = True
    config_file = None

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
}

dataset = Dataset("stream")

with DAG(
    dag_id="lets_stream_unsuccessfully", 
    catchup=False,
    default_args=default_args,
    max_active_runs=1,
    start_date=datetime(2022,1,1),
    schedule=[dataset],
) as dag:
    stream_job = KubernetesPodOperatorAsync(
        task_id="stream",
        cluster_context="docker-desktop",  # is ignored when in_cluster is set to True
        cmds=["/bin/sh", "-c", "sleep 30; exit 1"],
        config_file=config_file,
        get_logs=True,
        image="busybox",
        in_cluster=in_cluster,  # if set to true, will look in the cluster, if false, looks for file
        is_delete_operator_pod=True,
        name="stream",
        namespace=namespace,
        outlets=[dataset],
        poll_interval=20,
        retries=1,
        retry_delay=timedelta(seconds=10)
    )

    restart = EmptyOperator(
        task_id="restart",
        trigger_rule="all_done",
        outlets=[dataset]
    )

    mark_failed = BashOperator(
        task_id="mark_failed",
        trigger_rule="all_done",
        bash_command="echo Upstream stream job failed. Will now fail successfully; exit 1",
    )

    stream_job >> restart >> mark_failed