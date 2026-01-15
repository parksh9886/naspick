import yfinance as yf
import FinanceDataReader as fdr
import pandas as pd
import os
import time
from datetime import datetime, timedelta

# Create data directory
if not os.path.exists('data'):
    os.makedirs('data')

def get_sp500_tickers():
    """Fetch latest S&P 500 list from FinanceDataReader"""
    try:
        sp500 = fdr.StockListing('SP500')
        return sp500['Symbol'].tolist()
    except:
        return [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK.B", "UNH", "XOM",
            "JNJ", "JPM", "V", "PG", "MA", "HD", "CVX", "MRK", "ABBV", "PEP"
        ]

def fetch_data():
    tickers = get_sp500_tickers()
    
    # Clean tickers (remove duplicates etc)
    tickers = list(set(tickers))
    print(f"🚀 Starting Data Mining for {len(tickers)} tickers (5 Year Scope)")
    
    # 1. Price History (5 Years)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365*5 + 20) # 5 years + margin
    
    print("\n📊 Fetching Price History...")
    
    # Fix tickers for yfinance (BRK.B -> BRK-B)
    yf_tickers = [t.replace('.', '-') for t in tickers]
    
    try:
        # Download all at once
        price_data = yf.download(yf_tickers, start=start_date, end=end_date, group_by='ticker', auto_adjust=True)
        
        # Stack to make it long format: Date, Ticker, Close, Volume
        # yf.download result with group_by='ticker' has MultiIndex columns (Ticker, Price)
        # We need to restructure this
        
        formatted_data = []
        
        for ticker in yf_tickers:
            if ticker in price_data.columns.levels[0]:
                df = price_data[ticker].copy()
                df['Ticker'] = ticker
                df = df.reset_index()
                # Rename columns if needed (Close, Volume are standard)
                if 'Close' in df.columns and 'Volume' in df.columns:
                     formatted_data.append(df[['Date', 'Ticker', 'Close', 'Volume']])
                
        if formatted_data:
            all_prices = pd.concat(formatted_data)
            all_prices.to_csv('data/price_history.csv', index=False)
            print(f"✅ Saved price_history.csv ({len(all_prices)} rows)")
        else:
            print("❌ Failed to parse price data")
            
    except Exception as e:
        print(f"❌ Error fetching prices: {e}")

    # 2. Financials (Heavy Task)
    print("\n💰 Fetching Financials (This may take time)...")
    financial_data = []
    
    # IMPORTANT: yfinance often fails to get historical financials correctly via .info or .financials for free.
    # For this MVP backtest, we will use the CURRENT stats and assume they were constant or try to get trailing data.
    # A true backtest needs Point-in-Time data which is hard to get for free.
    # Strategy: Get current key metrics (PER, ROE, etc.) from .info and some history from .financials if possible.
    # For now, we will fetch 'info' which gives TTM (Trailing Twelve Months) data. 
    # This introduces some look-ahead bias (using today's PER for 1 year ago), but for "Phase 1" it's a starting point.
    # We can refine this later by scraping macrotrends if needed.
    
    for idx, ticker in enumerate(yf_tickers):
        print(f"[{idx+1}/{len(yf_tickers)}] {ticker}...", end="\r")
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Map info to our factors
            # Value: trailingPE, priceToBook, forwardPE, enterpriseToEbitda
            # Profitability: returnOnEquity, profitMargins, operatingMargins
            # Growth: revenueGrowth, earningsGrowth
            
            row = {
                "Ticker": ticker,
                "PER": info.get('trailingPE'),
                "Forward_PER": info.get('forwardPE'),
                "PBR": info.get('priceToBook'),
                "PSR": info.get('priceToSalesTrailing12Months'),
                "EV_EBITDA": info.get('enterpriseToEbitda'),
                "ROE": info.get('returnOnEquity'),
                "Profit_Margin": info.get('profitMargins'),
                "Oper_Margin": info.get('operatingMargins'),
                "Rev_Growth": info.get('revenueGrowth'),
                "EPS_Growth": info.get('earningsGrowth'),
                "Sector": info.get('sector', 'Unknown')
            }
            financial_data.append(row)
            
        except Exception as e:
            continue
            
    if financial_data:
        df_fin = pd.DataFrame(financial_data)
        df_fin.to_csv('data/financials.csv', index=False)
        print(f"\n✅ Saved financials.csv ({len(df_fin)} tickers)")
    else:
        print("\n❌ Failed to fetch financials")

if __name__ == "__main__":
    fetch_data()
