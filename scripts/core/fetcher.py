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
        # FDR may return tickers as BRKB or BRK-B, we normalize to BRK.B format
        for t in REQUIRED_TICKERS:
            t_hyphen = t.replace('.', '-')  # BRK.B -> BRK-B
            t_concat = t.replace('.', '')   # BRK.B -> BRKB
            
            # Remove any variant formats
            if t_hyphen in tickers:
                tickers.remove(t_hyphen)
            if t_concat in tickers:
                tickers.remove(t_concat)
            
            # Add the canonical dot format
            if t not in tickers:
                tickers.append(t)
                
        return sorted(list(set(tickers)))

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
            if idx % 50 == 0: print(f"   [{idx}/{len(tickers)}] Fetched...")
                
            for attempt in range(3):
                try:
                    fetch_ticker = self.fetch_map.get(ticker, ticker)
                    hist = fdr.DataReader(fetch_ticker, start_date, end_date)
                    
                    if hist.empty or len(hist) < 260: # Need ~1 year
                        if attempt < 2: 
                            time.sleep(1)
                            continue
                        else:
                            break # Fail after 3 attempts
                        
                    hist['Ticker'] = ticker
                    hist = hist[['Ticker', 'Open', 'High', 'Low', 'Close', 'Volume']]
                    hist.index.name = 'Date'
                    hist = hist.reset_index()
                    
                    all_hist_list.append(hist)
                    break # Success
                    
                except Exception as e:
                    if attempt < 2:
                        time.sleep(1)
                    else:
                        print(f"   ❌ Failed to fetch {ticker}: {e}")
                
        if not all_hist_list:
            return pd.DataFrame()
            
        return pd.concat(all_hist_list)

    def get_market_caps_bulk(self, tickers):
        """Fetch market cap for tickers using yfinance (Batch)"""
        print(f"💰 Fetching Market Caps for {len(tickers)} tickers via yfinance...")
        import yfinance as yf
        mcaps = {}
        
        chunk_size = 100
        for i in range(0, len(tickers), chunk_size):
            chunk = tickers[i:i+chunk_size]
            # Sanitize for yfinance
            yf_chunk = [t.replace('.', '-') for t in chunk]
            print(f"   Fetching market cap chunk {i//chunk_size + 1} ({len(yf_chunk)} stocks)...")
            
            try:
                batch = yf.Tickers(" ".join(yf_chunk))
                # Iterate through response
                for t_sym, ticker_obj in batch.tickers.items():
                    try:
                        # Map back to original ticker (hyphenated from yf)
                        # We need to match precise original ticker key
                        # The key in batch.tickers is usually the sanitized one (e.g. BRK-B)
                        
                        original_ticker = t_sym
                        # Reverse lookup if needed (simple Replace)
                        if '-' in t_sym and t_sym.replace('-', '.') in tickers:
                             original_ticker = t_sym.replace('-', '.')

                        info = ticker_obj.info
                        if info and 'marketCap' in info and info['marketCap']:
                             mcaps[original_ticker] = int(info['marketCap'])
                        else:
                             # Fallback fast exit
                             mcaps[original_ticker] = 0
                             
                    except Exception:
                        pass
            except Exception as e:
                print(f"❌ Error fetching market cap chunk: {e}")
                
        return mcaps

    def fetch_calendar_data_bulk(self, tickers):
        """Fetch Calendar (Earnings, Divs) for tickers using yfinance"""
        import yfinance as yf
        print(f"📅 Fetching Calendar Data for {len(tickers)} tickers...")
        
        chunk_size = 50
        calendar_data = {} # {ticker: {next_earnings, next_dividend_date, div_rate, div_yield}}
        
        # We need to act carefully as calling .calendar on Ticker object might trigger requests.
        # yf.Tickers might optimizes some access.
        
        for i in range(0, len(tickers), chunk_size):
            chunk = tickers[i:i+chunk_size]
            # [Fix] Sanitize tickers for yfinance (BRK.B -> BRK-B)
            yf_chunk = [t.replace('.', '-') for t in chunk]
            
            print(f"   Fetching extra info chunk {i//chunk_size + 1} ({len(yf_chunk)} stocks)...")
            
            try:
                tickers_obj = yf.Tickers(" ".join(yf_chunk))
                
                # yf.Tickers.tickers is a dict of Ticker objects
                for t_sym, ticker_obj in tickers_obj.tickers.items():
                    try:
                        data = {}
                        
                        # 1. Earnings (Improved with earnings_dates)
                        try:
                            # Try to get strictly future earnings from earnings_dates (DataFrame)
                            # This is more reliable than ticker.calendar which sometimes shows past dates
                            e_dates = ticker_obj.earnings_dates
                            found_future_earnings = False
                            
                            if e_dates is not None and not e_dates.empty:
                                try:
                                    # Normalize timezone to match earnings_dates index
                                    now = pd.Timestamp.now().tz_localize(e_dates.index.dtype.tz)
                                    # specific future earnings
                                    future_earnings = e_dates[e_dates.index >= now].sort_index()
                                    
                                    if not future_earnings.empty:
                                        # The first one is the nearest future earnings
                                        next_date = future_earnings.index[0]
                                        data['next_earnings'] = next_date.strftime('%Y-%m-%d')
                                        found_future_earnings = True
                                    
                                    # Also capture past earnings for 'Recent Results'
                                    past_earnings = e_dates[e_dates.index < now].sort_index(ascending=False)
                                    if not past_earnings.empty:
                                        last = past_earnings.iloc[0]
                                        if pd.notna(last['Reported EPS']):
                                            data['last_earnings_date'] = past_earnings.index[0].strftime('%Y-%m-%d')
                                            data['last_eps_est'] = float(last['EPS Estimate']) if pd.notna(last['EPS Estimate']) else None
                                            data['last_eps_act'] = float(last['Reported EPS'])
                                            data['last_surprise'] = float(last['Surprise(%)']) if pd.notna(last['Surprise(%)']) else None
                                except Exception as e:
                                    pass

                            # Fallback to .calendar if no future earnings found in dataframe
                            if not found_future_earnings:
                                cal = ticker_obj.calendar
                                if cal and 'Earnings Date' in cal:
                                    dates = cal['Earnings Date']
                                    if dates:
                                        data['next_earnings'] = dates[0].strftime('%Y-%m-%d')
                                        
                        except Exception:
                            pass
                        
                        # 2. Dividend Dates (Calendar + History fallback)
                        try:
                            cal = ticker_obj.calendar
                            # Ex-Dividend Date
                            if cal and 'Ex-Dividend Date' in cal:
                                d_date = cal['Ex-Dividend Date']
                                if hasattr(d_date, 'strftime'):
                                    data['ex_dividend_date'] = d_date.strftime('%Y-%m-%d')
                            
                            # Payment Date
                            if cal and 'Dividend Date' in cal:
                                p_date = cal['Dividend Date']
                                if hasattr(p_date, 'strftime'):
                                    data['dividend_payment_date'] = p_date.strftime('%Y-%m-%d')
                                    
                            # If no ex-dividend date from calendar (often empty if not declared),
                            # get the LAST ex-dividend date from history to show "Recent Div"
                            if 'ex_dividend_date' not in data:
                                divs = ticker_obj.dividends
                                if not divs.empty:
                                    # Last one
                                    last_div_date = divs.index[-1]
                                    data['ex_dividend_date'] = last_div_date.strftime('%Y-%m-%d')
                                    # Mark this as 'past' implicitly by date check in frontend, 
                                    # or we could add a flag, but date comparison is enough.
                                    
                        except Exception:
                            pass
                        
                        # 3. Dividend Amount (Per Share) & Annualized TTM
                        try:
                            divs = ticker_obj.dividends
                            if not divs.empty:
                                last_div = divs.iloc[-1]
                                data['dividend_amount'] = float(last_div)
                                
                                # [New] Calculate TTM Dividends (Last 365 days sum)
                                # This handles Monthly, Quarterly, Semi-Annual, Annual automatically
                                ttm_start = pd.Timestamp.now().tz_localize(divs.index.dtype.tz) - pd.Timedelta(days=365)
                                ttm_divs = divs[divs.index >= ttm_start]
                                if not ttm_divs.empty:
                                    data['dividend_ttm'] = float(ttm_divs.sum())
                                else:
                                    # Fallback if no divs in last year but has history (rare)
                                    # Just use frequency * last_div? Unsafe.
                                    # Just use last_div * 4 as very rough estimate if logic fails
                                    pass

                        except: pass
                        
                        # 4. Dividend Yield (Priority: info > TTM calculation)
                        try:
                            info = ticker_obj.info
                            if info and 'dividendYield' in info and info['dividendYield']:
                                raw_yield = info['dividendYield']
                                # [Fix] If yield > 0.5 (50%), it's likely already a percentage.
                                # Normally yields are 0.05 (5%), but sometimes 5.0 (5%).
                                if raw_yield > 0.5:
                                    data['dividend_yield'] = round(raw_yield, 2)
                                else:
                                    data['dividend_yield'] = round(raw_yield * 100, 2)
                            
                            # Fallback: Calculate from TTM
                            elif 'dividend_ttm' in data and 'previousClose' in info:
                                price = info['previousClose']
                                if price and price > 0:
                                     yield_val = (data['dividend_ttm'] / price) * 100
                                     data['dividend_yield'] = round(yield_val, 2)
                                     # data['is_ttm_yield'] = True
                        except: pass
                        
                        if data:
                            calendar_data[t_sym] = data
                            
                    except Exception as e:
                        pass
            except: pass
            
        return calendar_data
