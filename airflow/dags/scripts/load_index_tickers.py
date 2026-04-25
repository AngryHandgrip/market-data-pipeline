from scripts.db import dim_companies, get_engine
from massive import RESTClient
import pandas as pd
import requests
import logging
from io import StringIO
import time
from sqlalchemy import update, cast, Date, func
from sqlalchemy.dialects.postgresql import insert
import os

def load_montly_data():
    TARGET_INTERVAL = 12

    logger = logging.getLogger(__name__)

    api_key = os.getenv('MASSIVE_API_KEY')

    client = RESTClient(api_key)

    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'

    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        tables = pd.read_html(StringIO(response.text))
        df = tables[0]
        index_tickers = df['Symbol'][:5]
        logger.info('Список тикеров из S&P500 получен')
        engine = get_engine()

        updated = 0
        for i, ticker in enumerate(index_tickers):
            logger.info(f'[{i + 1}/{len(index_tickers)}] Загрузка данных для {ticker}')
            ticker_details = client.get_ticker_details(ticker)
            start_time = time.time()

            address_dict = None
            if ticker_details.address is not None:
                address_dict = {
                    "address1": ticker_details.address.address1,
                    "address2": ticker_details.address.address2,
                    "city": ticker_details.address.city,
                    "state": ticker_details.address.state,
                    "postal_code": ticker_details.address.postal_code,
                    "country": ticker_details.address.country
                }
            stmt = insert(dim_companies).values(
                ticker=ticker_details.ticker,
                name=ticker_details.name,
                is_active=ticker_details.active,
                industry=ticker_details.sic_description,
                exchange=ticker_details.primary_exchange,
                list_date=ticker_details.list_date,
                market_cap=ticker_details.market_cap,
                address=address_dict,
                description=ticker_details.description
            )
            upsert_stmt = stmt.on_conflict_do_update(
                index_elements=['ticker'],
                set_={
                    'name': stmt.excluded.name,
                    'is_active': stmt.excluded.is_active,
                    'industry': stmt.excluded.industry,
                    'exchange': stmt.excluded.exchange,
                    'list_date': stmt.excluded.list_date,
                    'market_cap': stmt.excluded.market_cap,
                    'address': stmt.excluded.address,
                    'updated_at': func.now()
                }
            )
            with engine.connect() as conn:
                conn.execute(upsert_stmt)
                conn.commit()

            logger.info(f'Данные по {ticker} загружены')

            updated += 1

            elapsed_time = time.time() - start_time
            time_to_wait = TARGET_INTERVAL - elapsed_time

            if time_to_wait > 0:
                time.sleep(time_to_wait)

        deactivate_tickers = update(dim_companies)
        deactivate_tickers = deactivate_tickers.values(is_active=False)
        deactivate_tickers = deactivate_tickers.where(cast(dim_companies.c.updated_at, Date) < func.current_date(),
                                                    dim_companies.c.is_active == True)
        with engine.connect() as conn:
            result = conn.execute(deactivate_tickers)
            conn.commit()
            deactivated = result.rowcount

        logger.info(f'Ежемесячное обновление завершено: обновлено {updated}, деактивировано {deactivated} тикеров')

    else:
        logger.error(f'Connection error.')


if __name__ == '__main__':
    load_montly_data()