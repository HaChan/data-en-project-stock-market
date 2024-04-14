import os
import yfinance as yf
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator
from datetime import datetime, timedelta
import pandas as pd
from io import BytesIO
from minio import Minio

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 3, 29),  # Adjust as needed
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def minio_client():
    return Minio(
        "minioserver:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )

def create_bucket(client, name):
    if not client.bucket_exists(name):
        client.make_bucket(name)


def fetch_symbols(bucket_name='stock-market', obj_name='list_symbols'):
    df = pd.read_csv("http://www.nasdaqtrader.com/dynamic/SymDir/nasdaqtraded.txt", sep='|')
    clean_df = df[df['Test Issue'] == 'N']
    print('Total number of symbols extracted:', clean_df['Symbol'].count())

    csv_buffer = BytesIO()
    clean_df.to_csv(csv_buffer, index=False)
    buffer_size = csv_buffer.tell()
    csv_buffer.seek(0)

    client = minio_client()
    create_bucket(client, bucket_name)

    client.put_object(
        bucket_name,
        obj_name,
        csv_buffer,
        length=buffer_size #csv_buffer.tell()
    )
    print(f'DataFrame saved successfully to Minio as {obj_name} in bucket {bucket_name}')

def download_historical_data(bucket_name='stock-market', obj_name='list_symbols', offset=0, limit=3000, period='max'):
    client = minio_client()
    create_bucket(client, bucket_name)
    response = client.get_object(bucket_name, obj_name)

    symbols_data = pd.read_csv(BytesIO(response.data))
    print(symbols_data)
    symbols = symbols_data['NASDAQ Symbol'].tolist()

    limit = limit if limit else len(symbols)
    end = min(offset + limit, len(symbols))

    for i in range(offset, end):
        symbol = symbols[i]
        sym_name = f'symbol_hist/{symbol}'
        try:
            stat = client.stat_object(bucket_name, sym_name)
            print(f"Object '{sym_name}' exists in bucket '{bucket_name}'.")
            continue
        except Exception as e:
            if 'NoSuchKey' in str(e):
                print(f"Object '{sym_name}' does not exist in bucket '{bucket_name}'.")
                download_then_upload_to_minio(symbol, period, client, bucket_name, sym_name)
            else:
                print(f"Error checking object existence: {e}")

def download_then_upload_to_minio(symbol, period, client, bucket_name, sym_name):
    try:
        data = yf.download(symbol, period=period)
    except Exception as e:
        print(f'Error downloading {symbol}: {e}')
        return

    if len(data.index) == 0:
        return

    data['symbol'] = symbol
    csv_buffer = BytesIO()
    data.to_csv(csv_buffer)
    buffer_size = csv_buffer.tell()
    csv_buffer.seek(0)

    client.put_object(
        bucket_name,
        sym_name,
        csv_buffer,
        length=buffer_size
    )
    #data.to_csv('dataset/hist/{}.csv'.format(s))
    print(f'Downloaded {symbol} to {sym_name}')

with DAG(
    dag_id='extract_symbol_list',
    default_args=default_args,
    schedule_interval=None,  # Run manually
) as dag:
    extract_symbols_task = PythonOperator(
        task_id='extract_symbols',
        python_callable=fetch_symbols,
        provide_context=True,
    )
    download_historical_data_task = PythonOperator(
        task_id='download_historical_data',
        python_callable=download_historical_data,
        provide_context=True,
        op_kwargs={'limit': None},
    )
    spark_minio_to_postgres = SparkSubmitOperator(
        task_id='spark_job',
        application='jobs/spark_load_from_minio_to_postgres.py',
        conn_id='spark_default',
        executor_memory='4g',
        jars='misc/hadoop-aws-3.3.1.jar,misc/postgresql-42.2.18.jar',
        executor_cores=2,
        packages='org.apache.hadoop:hadoop-aws:3.3.1,org.postgresql:postgresql:42.2.18',
    )

    extract_symbols_task >> download_historical_data_task >> spark_minio_to_postgres
