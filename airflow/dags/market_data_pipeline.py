from airflow.decorators import dag, task
from scripts.load_index_tickers import load_montly_data
from scripts.daily_ticker_summary import load_daily_data
from datetime import datetime, timedelta


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
}

@dag(
    default_args=default_args,
    description='Load ticker trade info',
    schedule='0 1 * * *',
    catchup=False)
def market_daily_quotes():
    @task()
    def run_daily_load():
        load_daily_data()

    run_daily_load()


@dag(
    default_args=default_args,
    description='Monthly company list update',
    schedule='0 0 1 * *',
    catchup=False)
def market_monthly_tickers():
    @task()
    def run_load_tickers():
        load_montly_data()

    run_load_tickers()


market_daily_quotes()
market_monthly_tickers()