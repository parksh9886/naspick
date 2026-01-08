#!/usr/bin/env python3
"""
Get full S&P 500 ticker list
"""
import FinanceDataReader as fdr

# Get S&P 500 list from FinanceDataReader
sp500 = fdr.StockListing('SP500')
tickers = sp500['Symbol'].tolist()

print(f"Total S&P 500 tickers: {len(tickers)}")
print("\nFirst 20 tickers:")
print(tickers[:20])

# Save to file
with open('sp500_tickers.txt', 'w') as f:
    for ticker in tickers:
        f.write(f'"{ticker}",\n')

print(f"\n✅ Saved {len(tickers)} tickers to sp500_tickers.txt")
