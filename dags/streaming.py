from datetime import datetime, timedelta
from airflow import DAG, Dataset
from airflow.configuration import conf
from astronomer.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperatorAsync

# from streaming import StreamingTimetable


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
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dataset = Dataset("stream")

with DAG(
    dag_id="lets_stream", 
    catchup=False,
    default_args=default_args,
    max_active_runs=1,
    start_date=datetime(2022,1,1),
    schedule=[dataset],
    # timetable=StreamingTimetable(dag_id=DAG_ID),
) as dag:
    KubernetesPodOperatorAsync(
        task_id="stream",
        poll_interval=20,
        image="busybox",
        cmds=["/bin/sh", "-c", "sleep 30", "bork"],
        name="stream",
        # resources=compute_resources,
        namespace=namespace,
        in_cluster=in_cluster,  # if set to true, will look in the cluster, if false, looks for file
        cluster_context="docker-desktop",  # is ignored when in_cluster is set to True
        config_file=config_file,
        # is_delete_operator_pod=True,
        get_logs=True,
        outlets=[dataset]
    )