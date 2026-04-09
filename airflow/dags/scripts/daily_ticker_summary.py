from scripts.db import dim_companies, fact_stock_prices, get_engine
import yfinance as yf
from sqlalchemy import select, join, func
from sqlalchemy.dialects.postgresql import insert
import datetime as dt


def load_daily_data():
    engine = get_engine()

    j = join(dim_companies, fact_stock_prices, dim_companies.c.ticker == fact_stock_prices.c.ticker, isouter=True)
    stmt = select(dim_companies.c.ticker, func.max(fact_stock_prices.c.date)).select_from(j).group_by(dim_companies.c.ticker)

    with engine.connect() as conn:
        active_tickers = conn.execute(stmt)

    download_batches = {}

    for ticker, last_date in active_tickers:
        if last_date is None:
            start_date = dt.date.today() - dt.timedelta(days=365)
        else:
            start_date = last_date + dt.timedelta(days=1)

        if start_date not in download_batches:
            download_batches[start_date] = []
        download_batches[start_date].append(ticker)

    for start_date, tickers in download_batches.items():
        if start_date > dt.date.today():
            continue

        df = yf.download(
            tickers=' '.join(tickers), 
            start=start_date, 
            end=dt.date.today(),
            group_by="ticker"
        )

        if not df.empty:
            df_flat = df.stack(level=0).reset_index()
            df_flat.columns = [col.lower() for col in df_flat.columns]
            df_flat = df_flat[['date', 'ticker', 'open', 'high', 'low', 'close', 'volume']]
            df_flat = df_flat.rename(columns={'open': 'open_price', 'high': 'high_price', 'low': 'low_price', 'close': 'close_price'})
            data = df_flat.to_dict(orient='records')

            stmt = insert(fact_stock_prices).values(data)
            stmt = stmt.on_conflict_do_nothing(index_elements=['date', 'ticker'])
        
        with engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()


if __name__ == '__main__':
    load_daily_data()