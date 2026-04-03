from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

with DAG(
    'market_daily_quotes',
    default_args=default_args,
    description='Load ticker trade info',
    schedule='0 1 * * *',
    catchup=False
) as dag_daily:

    run_daily_script = BashOperator(
        task_id='run_daily_load',
        bash_command='python /opt/airflow/dags/daily_ticker_summary.py',
    )

with DAG(
    'market_monthly_tickers',
    default_args=default_args,
    description='Monthly company list update',
    schedule='0 0 1 * *',
    catchup=False
) as dag_monthly:

    run_monthly_script = BashOperator(
        task_id='run_monthly_load',
        bash_command='python /opt/airflow/dags/load_index_tickers.py',
    )