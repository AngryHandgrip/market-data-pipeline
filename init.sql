CREATE SCHEMA IF NOT EXISTS market_data;

CREATE TABLE IF NOT EXISTS market_data.dim_companies (
	ticker VARCHAR(10) NOT NULL,
	"name" VARCHAR(100) NOT NULL,
	is_active BOOL NOT NULL,
	industry VARCHAR(100) NULL,
	exchange VARCHAR(50) NULL,
	list_date DATE NULL,
	market_cap INT8 NULL,
	address JSONB NULL,
	description TEXT NULL,
	updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NULL,
	CONSTRAINT dim_companies_pkey PRIMARY KEY (ticker)
);

CREATE TABLE IF NOT EXISTS market_data.fact_stock_prices (
	"date" DATE NOT NULL,
	ticker VARCHAR(10) NOT NULL,
	open_price NUMERIC(10, 4) NULL,
	close_price NUMERIC(10, 4) NULL,
	high_price NUMERIC(10, 4) NULL,
	low_price NUMERIC(10, 4) NULL,
	volume INT8 NULL,
	CONSTRAINT fact_stock_prices_pkey PRIMARY KEY (date, ticker),
	CONSTRAINT fact_stock_prices_ticker_fkey FOREIGN KEY (ticker) REFERENCES market_data.dim_companies(ticker)
);