# tickers.py

# A representative subset of S&P 500 and Nasdaq 100 tickers for demonstration.
# In a real production environment, this would be fetched dynamically or contained a full list.

NASDAQ_100 = [
    "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "GOOG", "META", "TSLA", "AVGO", "PEP",
    "COST", "CSCO", "TMUS", "CMCSA", "AMD", "ADBE", "NFLX", "INTC", "QCOM", "TXN",
    "HON", "AMGN", "SBUX", "ISRG", "MDLZ", "GILD", "ADP", "BKNG", "PANW", "VRTX"
    # ... Add more as needed
]

SP_500 = [
    "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META", "TSLA", "BRK-B", "UNH", "JNJ",
    "XOM", "JPM", "PG", "V", "LLY", "MA", "HD", "CVX", "MRK", "ABBV",
    "PEP", "KO", "BAC", "COST", "PFE", "AVGO", "MCD", "CSCO", "TMO", "WMT",
    "DIS", "ACN", "ABT", "DHR", "NFLX", "LIN", "NKE", "ORCL", "CMCSA", "VZ"
    # ... Add more as needed
]

def get_all_tickers():
    # Merge and deduplicate
    combined = list(set(NASDAQ_100 + SP_500))
    return combined
