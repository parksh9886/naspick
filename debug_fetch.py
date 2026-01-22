import FinanceDataReader as fdr
from datetime import datetime, timedelta

tickers = ['AAPL', 'MMM', 'ABT', 'INVALID_TICKER', 'BRK-B']
end_date = datetime.now()
start_date = end_date - timedelta(days=400)

for ticker in tickers:
    try:
        print(f"Fetching {ticker}...")
        df = fdr.DataReader(ticker, start_date, end_date)
        print(f"Result for {ticker}: {len(df)} rows")
        if len(df) < 260:
            print("  -> Too short!")
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
