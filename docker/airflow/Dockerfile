FROM apache/airflow:2.8.4
RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" \
    apache-airflow-providers-snowflake \
    apache-airflow-providers-postgres \
    snowflake-connector-python \
    apache-airflow-providers-airbyte \
    dbt-postgres==1.7.15 \
    astronomer-cosmos
