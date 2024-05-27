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

def gravar_no_s3(**kwargs):

    # Set the connection parameters for the Minio S3 bucket
    bucket_name = 'tmp'
    aws_hook = S3Hook(aws_conn_id='aws_default')
    client = aws_hook.get_conn()

    # Set the source and destination paths
    src = os.path.join(data_csv_directory, filename)

    # Load data into a DataFrame
    df = pd.read_csv(src)
    
    # Transform column names to lowercase
    df.columns = map(str.lower, df.columns)
    
    # Save the modified DataFrame to a temporary CSV file
    temp_file = os.path.join(data_csv_directory, 'temp_file.csv')
    df.to_csv(temp_file, index=False)
    
    # Upload the modified CSV file to S3
    client.upload_file(temp_file, bucket_name, filename)
   
    return temp_file
    #os.remove(temp_file)

def gravar_lake(**kwargs):
    
    temp_file = kwargs['ti'].xcom_pull(task_ids='gravar_no_s3')
    # Set the connection parameters for the Minio S3 bucket
    bucket_name = 'lake'
    aws_hook = S3Hook(aws_conn_id='aws_default')
    client = aws_hook.get_conn()
    
    # Set the source and destination paths
    src = os.path.join(data_csv_directory, temp_file)

    # Gerar o timestamp atual usando pendulum
    timestamp = pendulum.now().format('YYYYMMDDHHmmss')
    
    # Definir o nome do arquivo de destino com o timestamp
    filename = f"coffeeshopsales_{timestamp}.csv"
    
    # Upload the modified CSV file to S3
    client.upload_file(src, bucket_name, filename)
   
    os.remove(temp_file)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': pendulum.datetime(2024, 5, 10),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'aws_conn_id': 'aws_default'
}

with DAG('copy_cvs_to_s3',
         default_args=default_args,
         schedule_interval=None,
         catchup=False) as dag:

    gravar_s3_task = PythonOperator(
        task_id='gravar_no_s3',
        python_callable=gravar_no_s3,
        provide_context=True
    )

    airbyte_transfere_dados_dw = TaskGroup('airbyte_transfere_dados_dw', dag=dag)

    # To get the connection id, go to your connection in airbyte
    # http://localhost:56174/workspaces/e46c12b3-10ad-4711-be3d-ba57ed4c0a15/connections/24886e0c-8467-404d-aaca-dabc888dcd15/status 
    # The string value after connection and before status is the connection_id
    airbyte_trigger_sync  = AirbyteTriggerSyncOperator(
        task_id="airbyte_trigger_sync",
        airbyte_conn_id='airbyte_default',
        connection_id='82a3937d-a76d-4ea4-8bb6-45b4491ce4d7',
        asynchronous=True,
        task_group=airbyte_transfere_dados_dw
    )

    airbyte_monitor_sync = AirbyteJobSensor(
        task_id="airbyte_monitor_sync",
        airbyte_conn_id='airbyte_default',
        airbyte_job_id=airbyte_trigger_sync.output,
        task_group=airbyte_transfere_dados_dw
    )

    dbt_transforma_dw = TaskGroup('dbt_transforma_dw',dag=dag)

    run_dbt_bronze_models = BashOperator(
        task_id='run_dbt_bronze_models',
        bash_command=run_command + " --select bronze",
        task_group=dbt_transforma_dw
    )

    run_dbt_silver_models = BashOperator(
        task_id='run_dbt_silver_models',
        bash_command=run_command + " --select silver",
        task_group=dbt_transforma_dw
    )

    run_dbt_gold_models = BashOperator(
        task_id='run_dbt_gold_models',
        bash_command=run_command + " --select gold",
        task_group=dbt_transforma_dw
    )

    gravar_s3_lake_task = PythonOperator(
        task_id='gravar_s3_lake_task',
        python_callable=gravar_lake,
        provide_context=True
    )

end = EmptyOperator(task_id="end")

start >> gravar_s3_task >> airbyte_trigger_sync >> airbyte_monitor_sync >> run_dbt_bronze_models >> run_dbt_silver_models >> run_dbt_gold_models >> gravar_s3_lake_task >> end