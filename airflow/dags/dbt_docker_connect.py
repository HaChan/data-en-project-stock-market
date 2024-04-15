import os
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime, timedelta
from docker.types import Mount

dbt_path = os.getenv('DBT_PATH')

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 3, 29),
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}
with DAG(
    'dbt_docker',
    default_args=default_args,
    schedule_interval=None,
) as dag:
    docker_task = DockerOperator(
        task_id='dbt_run',
        image='dbt-stock-market',
        api_version='auto',
        auto_remove=True,
        command='debug',
        docker_url='tcp://host.docker.internal:2375',
        network_mode='stock-market-network',
        mount_tmp_dir=False,
        mounts=[
            Mount(source=dbt_path, target='/usr/app/dbt/', type="bind"),
            Mount(source=f"{dbt_path}/profiles.yml", target='/root/.dbt/profiles.yml', type="bind"),
        ]
    )

    docker_task
