FROM apache/airflow:3.1.8

RUN pip install --no-cache-dir sqlalchemy pandas yfinance psycopg2-binary requests massive