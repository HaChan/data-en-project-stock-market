import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor
from datetime import datetime, timedelta
import pandas as pd

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 3, 29),  # Adjust as needed
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}
airflow_home = os.getenv('AIRFLOW_HOME', '/opt/airflow')
symbol_list_file = os.path.join(airflow_home, 'dataset/symbols_valid_meta.csv')

def fetch_symbols():
    data = pd.read_csv("http://www.nasdaqtrader.com/dynamic/SymDir/nasdaqtraded.txt", sep='|')
    data_clean = data[data['Test Issue'] == 'N']
    symbols = data_clean['NASDAQ Symbol'].tolist()
    valid_data = pd.DataFrame({'symbol': symbols})
    valid_data.to_csv(symbol_list_file, index=False)
    print('Total number of symbols extracted:', len(symbols))

def download_historical_data(file_path, offset=0, limit=3000, period='max'):
    symbols_data = pd.read_csv(file_path)
    symbols = symbols_data['NASDAQ Symbol'].tolist()

    limit = limit if limit else len(symbols)
    end = min(offset + limit, len(symbols))
    is_valid = [False] * len(symbols)

    for i in range(offset, end):
        s = symbols[i]
        data = yf.download(s, period=period)
        if len(data.index) == 0:
            continue

        is_valid[i] = True
        data.to_csv('dataset/hist/{}.csv'.format(s))
    print('Total number of valid symbols downloaded:', sum(is_valid))

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
    file_sensor_task = FileSensor(
        task_id='wait_for_symbols_file',
        filepath=symbol_list_file,
        timeout=60
    )
    download_historical_data_task = PythonOperator(
        task_id='download_historical_data',
        python_callable=download_historical_data,
        provide_context=True,
        trigger_rule='one_success',
        op_kwargs={'file_path': symbol_list_file},
    )

    extract_symbols_task >> file_sensor_task >> download_historical_data_task
