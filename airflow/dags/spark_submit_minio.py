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
        application='jobs/minio_spark_example.py',
        conn_id='spark_default',
        executor_memory='4g',
        jars='misc/hadoop-aws-3.3.1.jar',
        executor_cores=2,
        packages='org.apache.hadoop:hadoop-aws:3.3.1',
        application_args=['arg1', 'arg2']
    )
    spark_task
