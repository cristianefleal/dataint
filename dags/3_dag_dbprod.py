import pendulum
from airflow import DAG
from airflow.models import Variable
from airflow.operators.python_operator import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.airbyte.operators.airbyte import AirbyteTriggerSyncOperator
from airflow.providers.airbyte.sensors.airbyte import AirbyteJobSensor
from airflow.utils.task_group import TaskGroup
from airflow.operators.bash_operator import BashOperator
import json
import os
import pandas as pd

dag_path = os.path.join(os.path.dirname(__file__))
data_csv_directory = f'/opt/airflow/data'
filename = 'coffeeshopsales.csv' 

project_name = 'impacta'
dbt_directory = f'/opt/airflow/dbt/'
dbt_project = f'/{dbt_directory}/{project_name}'

# RUN
run_command = f"\
    dbt run \
    --profiles-dir {dbt_directory} \
    --project-dir {dbt_project} \
    --target prod_airflow "

start = EmptyOperator(task_id="start")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': pendulum.datetime(2024, 5, 10),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'aws_conn_id': 'aws_default'
}

with DAG('3_dbstage_to_dbprod',
         default_args=default_args,
         schedule_interval=None,
         catchup=False) as dag:

    # To get the connection id, go to your connection in airbyte
    # http://localhost:56174/workspaces/e46c12b3-10ad-4711-be3d-ba57ed4c0a15/connections/24886e0c-8467-404d-aaca-dabc888dcd15/status 
    # The string value after connection and before status is the connection_id
    airbyte_trigger_sync  = AirbyteTriggerSyncOperator(
        task_id="airbyte_trigger_sync",
        airbyte_conn_id='airbyte_default',
        connection_id='3166fdd1-bc72-4aef-a0b9-c3cf5fc81cc0',
        asynchronous=True,

    )

    airbyte_monitor_sync = AirbyteJobSensor(
        task_id="airbyte_monitor_sync",
        airbyte_conn_id='airbyte_default',
        airbyte_job_id=airbyte_trigger_sync.output,

    )

end = EmptyOperator(task_id="end")

start >> airbyte_trigger_sync >> airbyte_monitor_sync >>  end