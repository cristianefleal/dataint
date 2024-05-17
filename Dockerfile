FROM apache/airflow:2.8.4
RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" apache-airflow-providers-snowflake snowflake-connector-python


