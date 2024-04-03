from airflow import DAG
from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 4, 2),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG('spark_dag', default_args=default_args, schedule_interval=None) as dag:
    spark_task = SparkSubmitOperator(
        task_id='spark_job',
        application='spark_submit_minio.py',
        conn_id='spark_default',
        executor_memory='4g',
        executor_cores=2,
        application_args=['arg1', 'arg2']
    )
    spark_task
