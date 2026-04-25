from sqlalchemy import create_engine, MetaData, Table, Column, String, Boolean, BigInteger, Date, Text, DateTime, Numeric
from sqlalchemy.dialects.postgresql import JSONB
import os


def get_engine():
    password = os.getenv('DB_PASSWORD')
    return create_engine(f'postgresql://user:{password}@data-postgres:5432/market_db')

metadata = MetaData(schema='market_data')

dim_companies = Table(
    'dim_companies', metadata,
    Column('ticker', String(10), primary_key=True),
    Column('name', String(100)),
    Column('is_active', Boolean),
    Column('industry', String(100)),
    Column('exchange', String(50)),
    Column('list_date', Date),
    Column('market_cap', BigInteger),
    Column('address', JSONB),
    Column('description', Text),
    Column('updated_at', DateTime)
)

fact_stock_prices = Table(
    'fact_stock_prices', metadata,
    Column('date', Date, primary_key=True),
    Column('ticker', String(10), primary_key=True),
    Column('open_price', Numeric(10, 4)),
    Column('close_price', Numeric(10, 4)),
    Column('high_price', Numeric(10, 4)),
    Column('low_price', Numeric(10, 4)),
    Column('volume', BigInteger)
)
