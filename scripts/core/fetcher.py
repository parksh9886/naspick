import FinanceDataReader as fdr
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
from scripts.config import FETCH_MAP, REQUIRED_TICKERS, FALLBACK_TICKERS, SECTOR_OVERRIDES, EXCHANGE_OVERRIDES

class StockDataFetcher:
    """
    Handles all external API interactions to fetch stock data.
    - S&P 500 Ticker List
    - Sector & Exchange Info
    - Price History (OHLCV)
    - Market Caps
    """
    
    def __init__(self):
        self.fetch_map = FETCH_MAP
    
    def get_sp500_tickers(self):
        """Fetch latest S&P 500 list from FinanceDataReader"""
        try:
            sp500 = fdr.StockListing('SP500')
            tickers = sp500['Symbol'].tolist()
        except:
            # Fallback
            tickers = FALLBACK_TICKERS[:]
            
        # Ensure dual class shares logic
        for t in REQUIRED_TICKERS:
            t_hyphen = t.replace('.', '-')
            if t_hyphen in tickers:
                tickers.remove(t_hyphen)
            if t not in tickers:
                tickers.append(t)
                
        return list(set(tickers))

    def get_sector_data(self):
        """Fetch sector data mapping"""
        try:
            sp500 = fdr.StockListing('SP500')
            sectors = dict(zip(sp500['Symbol'], sp500['Sector']))
            # Manual overrides
            for t, sec in SECTOR_OVERRIDES.items():
                sectors[t] = sec
            return sectors
        except:
            return {}

    def get_exchange_data(self):
        """Fetch exchange listings (NASDAQ, NYSE, AMEX)"""
        exchanges = {}
        try:
            # Try catch blocks for each to survive individual failures
            try:
                nasdaq = fdr.StockListing('NASDAQ')
                for t in nasdaq['Symbol']: exchanges[t] = 'NASDAQ'
            except: pass
            
            try:
                nyse = fdr.StockListing('NYSE')
                for t in nyse['Symbol']: exchanges[t] = 'NYSE'
            except: pass
            
            try:
                amex = fdr.StockListing('AMEX')
                for t in amex['Symbol']: exchanges[t] = 'AMEX'
            except: pass
            
            # Manual overrides
            for t, exc in EXCHANGE_OVERRIDES.items():
                exchanges[t] = exc
            
            return exchanges
        except:
            return {}

    def fetch_price_history_bulk(self, tickers, days=400):
        """Fetch OHLCV data for multiple tickers"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        all_hist_list = []
        print(f"📊 Fetching Price Data for {len(tickers)} tickers...")
        
        for idx, ticker in enumerate(tickers, 1):
            try:
                if idx % 50 == 0: print(f"   [{idx}/{len(tickers)}] Fetched...")
                
                fetch_ticker = self.fetch_map.get(ticker, ticker)
                hist = fdr.DataReader(fetch_ticker, start_date, end_date)
                
                if hist.empty or len(hist) < 260: # Need ~1 year
                    continue
                    
                hist['Ticker'] = ticker
                hist = hist[['Ticker', 'Open', 'High', 'Low', 'Close', 'Volume']]
                hist.index.name = 'Date'
                hist = hist.reset_index()
                
                all_hist_list.append(hist)
                
            except Exception:
                continue
                
        if not all_hist_list:
            return pd.DataFrame()
            
        return pd.concat(all_hist_list)

    def get_market_caps_bulk(self, tickers):
        """Fetch market cap for tickers"""
        print(f"💰 Fetching Market Caps for {len(tickers)} tickers...")
        mcaps = {}
        
        try:
            # Fetch broad listings containing MarCap
            df_nasdaq = fdr.StockListing('NASDAQ')
            df_nyse = fdr.StockListing('NYSE')
            df_amex = fdr.StockListing('AMEX')
            
            combined = pd.concat([df_nasdaq, df_nyse, df_amex])
            
            col = 'MarCap' if 'MarCap' in combined.columns else 'MarketCap'
            if col in combined.columns:
                mc_lookup = dict(zip(combined['Symbol'], combined[col]))
                
                for t in tickers:
                    mc = mc_lookup.get(t)
                    if not mc:
                        # Try hyphenated lookup
                        mc = mc_lookup.get(t.replace('.', '-'))
                    
                    mcaps[t] = int(mc) if mc else 0
            else:
                pass # Return empty maps or 0s
                
        except Exception as e:
            print(f"❌ Error fetching market cap: {e}")
            
        return mcaps
