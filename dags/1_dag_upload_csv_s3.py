import pendulum
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
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

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': pendulum.datetime(2024, 5, 10),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'aws_conn_id': 'aws_default'
}

with DAG('1_copy_cvs_to_s3',
         default_args=default_args,
         schedule_interval=None,
         catchup=False) as dag:

    gravar_s3_task = PythonOperator(
        task_id='gravar_no_s3',
        python_callable=gravar_no_s3,
        provide_context=True
    )

end = EmptyOperator(task_id="end")

start >> gravar_s3_task >> end
