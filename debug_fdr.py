import FinanceDataReader as fdr
try:
    sp500 = fdr.StockListing('SP500')
    print(f"SP500 Count: {len(sp500)}")
    print("First 10:", sp500['Symbol'].tolist()[:10])
except Exception as e:
    print(f"Error fetching SP500: {e}")
