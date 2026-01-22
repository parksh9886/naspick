import os

# --------------------------------------------------------------------------------
# PATHS & DIRECTORIES
# --------------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Project Root
DATA_DIR = os.path.join(BASE_DIR, 'data')

PATHS = {
    "FINANCIAL_INFO": os.path.join(DATA_DIR, 'financials.csv'),
    "RANKING_HISTORY": os.path.join(DATA_DIR, 'ranking_history.csv'),
    "OUTPUT_JSON": os.path.join(DATA_DIR, 'data.json'),
    "RANKS_JSON": os.path.join(DATA_DIR, 'yesterday_ranks.json'),
    "CONSENSUS_JSON": os.path.join(DATA_DIR, 'consensus_data.json'),
    "PORTFOLIO_STATE": os.path.join(DATA_DIR, 'portfolio_state.json'),
    "CHART_DATA": os.path.join(DATA_DIR, 'chart_data.json'),
    "SIGNALS_JSON": os.path.join(DATA_DIR, 'signals.json'),
}

# --------------------------------------------------------------------------------
# TICKER MANAGEMENT
# --------------------------------------------------------------------------------
# Yahoo Finance Fetch Mapping (Dot to Hyphen)
FETCH_MAP = {
    'BRK.B': 'BRK-B',
    'BF.B': 'BF-B'
}

# Dual Class Shares & Special Handling
REQUIRED_TICKERS = ['BRK.B', 'BF.B', 'GOOGL', 'GOOG', 'FOXA', 'FOX', 'NWSA', 'NWS']

# Fallback S&P 500 List (if API fails)
FALLBACK_TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK.B", "UNH", "XOM",
    "JNJ", "JPM", "V", "PG", "MA", "HD", "CVX", "MRK", "ABBV", "PEP"
]

# --------------------------------------------------------------------------------
# SECTOR & EXCHANGE MAPPING
# --------------------------------------------------------------------------------
# English to Korean Sector Names
SECTOR_TRANS_MAP = {
    "Technology": "기술", "Information Technology": "기술",
    "Communication Services": "커뮤니케이션",
    "Consumer Cyclical": "임의소비재", "Consumer Discretionary": "임의소비재",
    "Consumer Defensive": "필수소비재", "Consumer Staples": "필수소비재",
    "Energy": "에너지", "Financial Services": "금융", "Financial": "금융", "Financials": "금융",
    "Healthcare": "헬스케어", "Health Care": "헬스케어",
    "Industrials": "산업재", "Basic Materials": "소재", "Materials": "소재",
    "Real Estate": "부동산", "Utilities": "유틸리티"
}

# Manual Sector Overrides
SECTOR_OVERRIDES = {
    'BRK.B': 'Financials',
    'BF.B': 'Consumer Staples'
}

# Manual Exchange Overrides
EXCHANGE_OVERRIDES = {
    'BRK.B': 'NYSE',
    'BF.B': 'NYSE',
    'DAY': 'NYSE'
}
