"""
5-Year Backtest with Dividend Reinvestment (v3.1 - Adjusted Close Method)
- Uses Adjusted Close prices to simulate Total Return (Dividends Reinvested + Splits Handled)
- This is the standard industry method for backtesting Total Return.
- Recalculates scores daily
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
import json
from datetime import datetime
import yfinance as yf
from scripts.core.scorer import MarketScorer

# ===== CONFIG =====
INITIAL_CAPITAL = 100000
TOP_N = 10
EXIT_RANK = 20
MAX_POSITIONS = 20
FEE_RATE = 0.0025  # 0.25%
START_DATE = "2020-01-01" 

def load_financials():
    df = pd.read_csv('data/financials.csv')
    return df

def load_consensus():
    with open('data/consensus_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def get_sp500_tickers():
    with open('data/data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return [d['ticker'] for d in data]

def fetch_data_adjusted(tickers, start_date, end_date):
    print(f"📈 Fetching Adjusted Price data (Total Return): {start_date} to {end_date}")
    
    chunk_size = 50
    all_data = {}
    
    for i in range(0, len(tickers), chunk_size):
        chunk = tickers[i:i+chunk_size]
        print(f"   Fetching chunk {i//chunk_size + 1}/{(len(tickers)-1)//chunk_size + 1}...")
        
        try:
            # auto_adjust=True (default) gets Adjusted Close (Splits + Divs applied to past)
            df = yf.download(chunk, start=start_date, end=end_date, group_by='ticker', progress=False, threads=True, auto_adjust=True)
            
            for ticker in chunk:
                if len(chunk) == 1:
                    t_df = df
                else:
                    try:
                        t_df = df[ticker].copy()
                    except KeyError:
                        continue
                
                if t_df.empty or 'Close' not in t_df.columns:
                    continue
                    
                t_df = t_df.dropna(how='all')
                t_df['Ticker'] = ticker
                t_df = t_df.reset_index()
                
                # Cols needed: Date, Ticker, Close (Adj), Open/High/Low/Volume (Adj)
                # Note: With auto_adjust=True, OHLC are all adjusted.
                cols_needed = ['Date', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Volume']
                
                # Ensure all exist
                for c in cols_needed:
                    if c not in t_df.columns:
                        t_df[c] = 0
                
                all_data[ticker] = t_df[cols_needed]
                
        except Exception as e:
            print(f"⚠️ Chunk failed: {e}")
            
    print(f"✓ Fetched data for {len(all_data)} tickers")
    return all_data

def run_backtest():
    print("=" * 60)
    print("🧪 Backtest v3.1: Adjusted Close (Total Return)")
    print("   Starting from 2020-12-24")
    print("=" * 60)
    
    scorer = MarketScorer()
    financials = load_financials()
    consensus = load_consensus()
    
    end_date = datetime.now()
    start_date = datetime.strptime(START_DATE, '%Y-%m-%d')
    tickers = get_sp500_tickers()
    
    # 1. Fetch Data (Adjusted)
    data_map = fetch_data_adjusted(tickers, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    
    if not data_map: return

    # 2. Combine
    print("🔄 Preparing data for scorer...")
    combined_list = []
    for t, df in data_map.items():
        combined_list.append(df)
    
    price_df = pd.concat(combined_list, ignore_index=True)
    price_df['Date'] = pd.to_datetime(price_df['Date'])
    price_df = price_df.sort_values(['Date', 'Ticker'])
    
    # 3. Technicals
    print("📊 Calculating technical factors...")
    price_df = scorer.calculate_technical_factors_bulk(price_df)
    
    # 4. Simulation
    trading_days = sorted(price_df['Date'].unique())
    trading_days = [d for d in trading_days if d >= pd.Timestamp("2020-12-24")]
    
    cash = INITIAL_CAPITAL
    portfolio = {} 
    history = []
    trades = []
    
    rebalance_idx = 0
    
    print(f"📅 Simulation start: {trading_days[0].date()} to {trading_days[-1].date()}")
    
    for date in trading_days:
        date_str = date.strftime('%Y-%m-%d')
        
        # No explicit dividend processing needed (prices are adjusted)
        
        # Rebalance Weekly
        rebalance_idx += 1
        if rebalance_idx >= 5:
            rebalance_idx = 0
            
            daily_df = price_df[price_df['Date'] == date].copy()
            if len(daily_df) > 100:
                try:
                    scored_df = scorer.apply_sector_scoring(daily_df, financials, consensus)
                    
                    if not scored_df.empty:
                        rank_map = dict(zip(scored_df['Ticker'], scored_df['Rank']))
                        price_map = dict(zip(scored_df['Ticker'], scored_df['Close']))
                        
                        # Sell
                        to_sell = []
                        for ticker in list(portfolio.keys()):
                            if ticker not in rank_map or rank_map[ticker] > EXIT_RANK:
                                to_sell.append(ticker)
                        
                        for ticker in to_sell:
                            if ticker in price_map:
                                price = price_map[ticker]
                                qty = portfolio[ticker]['qty']
                                proceeds = qty * price * (1 - FEE_RATE)
                                cash += proceeds
                                trades.append({"date": date_str, "type": "SELL", "ticker": ticker})
                            del portfolio[ticker]
                        
                        # Buy
                        open_slots = MAX_POSITIONS - len(portfolio)
                        if open_slots > 0:
                            curr_val = cash + sum(p['qty'] * price_map.get(t, 0) for t, p in portfolio.items())
                            target_alloc = curr_val / MAX_POSITIONS
                            
                            candidates = scored_df[scored_df['Rank'] <= TOP_N].sort_values('Rank')
                            for _, row in candidates.iterrows():
                                if open_slots <= 0: break
                                ticker = row['Ticker']
                                if ticker in portfolio: continue
                                
                                price = row['Close']
                                if cash > target_alloc * 0.9:
                                    qty = int(target_alloc / (price * (1 + FEE_RATE)))
                                    if qty > 0:
                                        cost = qty * price * (1 + FEE_RATE)
                                        cash -= cost
                                        portfolio[ticker] = {'qty': qty, 'cost': cost}
                                        open_slots -= 1
                                        trades.append({"date": date_str, "type": "BUY", "ticker": ticker})
                except:
                    pass

        # Record History
        current_val = cash
        for ticker, pos in portfolio.items():
            if ticker in data_map:
                t_df = data_map[ticker]
                row = t_df[t_df['Date'] == date]
                if not row.empty:
                    current_val += pos['qty'] * row.iloc[0]['Close']
                else:
                    current_val += pos['cost'] # Fallback
            else:
                current_val += pos['cost']
                
        history.append({
            "date": date_str,
            "value": round(current_val, 2)
        })

    # Saving Results
    final_val = history[-1]['value']
    total_ret = (final_val - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100
    
    print("\n" + "="*50)
    print("📊 BACKTEST v3.1 RESULT (Total Return)")
    print("="*50)
    print(f"💰 Final Value:    ${final_val:,.0f}")
    print(f"📈 Total Return:   {total_ret:.1f}%")
    print("-" * 50)
    
    # Save chart_data.json
    print("🔄 Fetching SPY for Charting...")
    spy_df = yf.download('SPY', start=trading_days[0], end=datetime.now(), auto_adjust=True, progress=False)
    if isinstance(spy_df.columns, pd.MultiIndex):
        try: spy_df = spy_df.xs('SPY', axis=1, level=0)
        except: pass
        
    chart_data = []
    for h in history:
        d = h['date']
        try:
            ts = pd.Timestamp(d)
            if ts in spy_df.index:
                val = spy_df.loc[ts]['Close']
            else:
                val = spy_df.iloc[spy_df.index.get_indexer([ts], method='nearest')[0]]['Close']
            if hasattr(val, 'item'): val = val.item()
        except: val = 0
            
        chart_data.append({
            "date": d,
            "sb1": h['value'],
            "spy": float(val)
        })
        
    with open('data/chart_data.json', 'w', encoding='utf-8') as f:
        json.dump(chart_data, f, indent=2)
    print("✅ chart_data.json updated")
    
    # Sync Portfolio State
    print("🔄 Syncing portfolio state...")
    try:
        with open('data/data.json', 'r', encoding='utf-8') as f:
            d_json = json.load(f)
        top10 = sorted(d_json, key=lambda x: x['rank'])[:10]
        
        eq_val = final_val * 0.9
        cash_val = final_val * 0.1
        per_stock = eq_val / 10
        
        new_holdings = {}
        spent = 0
        for s in top10:
            # Need current price. data.json has it.
            # But wait, data.json has price from 'fdr' (unadjusted).
            # This is fine for 'Quantity' calculation for *today*.
            p = s.get('current_price', 0)
            if p > 0:
                q = int(per_stock / p)
                new_holdings[s['ticker']] = q
                spent += q * p
        
        real_cash = final_val - spent
        
        state = {
            "last_update": datetime.now().strftime("%Y-%m-%d"),
            "cash": round(real_cash, 2),
            "total_value": round(final_val, 2),
            "holdings": new_holdings,
            "note": f"Synced with Backtest v3.1 (Total Return) on {datetime.now().date()}"
        }
        with open('data/portfolio_state.json', 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
        print("✅ data/portfolio_state.json synced")
    except Exception as e:
        print(f"⚠️ Sync error: {e}")

if __name__ == "__main__":
    run_backtest()
