"""
5-Year Backtest with Dividend Reinvestment (v3.0)
- Fetches 5+ years of price AND dividend data using yfinance
- Reinvests dividends into cash pool (Tax not deducted to match Gross TR Index, or can verify)
- Recalculates scores daily
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import yfinance as yf
from scripts.core.scorer import MarketScorer

# ===== CONFIG =====
INITIAL_CAPITAL = 100000
TOP_N = 10
EXIT_RANK = 20
MAX_POSITIONS = 20
FEE_RATE = 0.0025  # 0.25%
START_DATE = "2020-01-01"  # Warmup start

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

def fetch_data_with_dividends(tickers, start_date, end_date):
    print(f"📈 Fetching Price & Dividend data: {start_date} to {end_date}")
    
    # Chunking to avoid massive requests failing
    chunk_size = 50
    all_data = {}
    
    for i in range(0, len(tickers), chunk_size):
        chunk = tickers[i:i+chunk_size]
        print(f"   Fetching chunk {i//chunk_size + 1}/{(len(tickers)-1)//chunk_size + 1}...")
        
        try:
            # actions=True fetches Dividends and Splits
            # auto_adjust=False to get Raw Price + Dividends (Manual Reinvestment)
            df = yf.download(chunk, start=start_date, end=end_date, actions=True, auto_adjust=False, group_by='ticker', progress=False, threads=True)
            
            # Reorganize data: Dict of DataFrames {Ticker: DF}
            for ticker in chunk:
                if len(chunk) == 1:
                    t_df = df
                else:
                    try:
                        t_df = df[ticker].copy()
                    except KeyError:
                        continue
                
                # Check if empty (sometimes yf returns NaNs for failed tickers)
                if t_df.empty or 'Close' not in t_df.columns:
                    continue
                    
                # Clean up
                t_df = t_df.dropna(how='all')
                t_df['Ticker'] = ticker
                t_df = t_df.reset_index() # Date becomes column
                
                # Ensure Dividends column exists
                if 'Dividends' not in t_df.columns:
                    t_df['Dividends'] = 0.0
                
                # Fill NaN dividends with 0
                t_df['Dividends'] = t_df['Dividends'].fillna(0)
                
                # Standardize columns
                cols_needed = ['Date', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Volume', 'Dividends']
                # Rename if needed (yf uses 'Date' as index name usually)
                
                all_data[ticker] = t_df[cols_needed]
                
        except Exception as e:
            print(f"⚠️ Chunk failed: {e}")
            
    print(f"✓ Fetched data for {len(all_data)} tickers")
    return all_data

def run_backtest():
    print("=" * 60)
    print("🧪 Backtest v3.0: Dividend Reinvestment")
    print("   Starting from 2020-12-24")
    print("=" * 60)
    
    scorer = MarketScorer()
    financials = load_financials()
    consensus = load_consensus()
    
    end_date = datetime.now()
    start_date = datetime.strptime(START_DATE, '%Y-%m-%d')
    
    tickers = get_sp500_tickers()
    
    # 1. Fetch Data
    # Map: Ticker -> DataFrame
    data_map = fetch_data_with_dividends(tickers, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    
    if not data_map:
        print("❌ No data fetched!")
        return

    # 2. Combine for technical calculation
    # Scorer expects one big DF with 'Ticker', 'Date', 'Close', etc.
    print("🔄 Preparing data for scorer...")
    combined_list = []
    for t, df in data_map.items():
        # Keep only price cols for scorer
        combined_list.append(df[['Date', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Volume']])
    
    if not combined_list:
        print("❌ Data merge failed")
        return
        
    price_df = pd.concat(combined_list, ignore_index=True)
    price_df['Date'] = pd.to_datetime(price_df['Date'])
    price_df = price_df.sort_values(['Date', 'Ticker'])
    
    # 3. Calculate Technicals
    print("📊 Calculating technical factors...")
    price_df = scorer.calculate_technical_factors_bulk(price_df)
    
    # 4. Simulation Setup
    trading_days = sorted(price_df['Date'].unique())
    trading_days = [d for d in trading_days if d >= pd.Timestamp("2020-12-24")]
    
    cash = INITIAL_CAPITAL
    portfolio = {} # {ticker: {'qty': int, 'cost': float}}
    history = []
    trades = []
    total_dividends = 0.0
    
    # Rebalance every 5 trading days
    rebalance_idx = 0
    
    print(f"📅 Simulation start: {trading_days[0].date()} to {trading_days[-1].date()}")
    
    for date in trading_days:
        date_str = date.strftime('%Y-%m-%d')
        
        # --- A. Process Dividends (Daily) ---
        msgs = []
        for ticker, pos in portfolio.items():
            if ticker in data_map:
                t_df = data_map[ticker]
                # Find row for today
                # Optimize: Convert 'Date' to index in data_map for faster lookup? 
                # For now boolean indexing is slow but safe.
                # BETTER: Filter t_df once? No, loop is daily.
                # Let's rely on efficient lookup.
                row = t_df[t_df['Date'] == date]
                if not row.empty:
                    div = row.iloc[0]['Dividends']
                    if div > 0:
                        amount = div * pos['qty']
                        cash += amount
                        total_dividends += amount
                        msgs.append(f"+ Div: {ticker} ${amount:.2f}")
        
        if msgs and len(msgs) < 3: # Log if few
             # print( f"   {date_str}: {', '.join(msgs)}")
             pass
        
        # --- B. Rebalance Logic (Weekly) ---
        rebalance_idx += 1
        if rebalance_idx >= 5:
            rebalance_idx = 0
            
            # Get Daily Slice
            daily_df = price_df[price_df['Date'] == date].copy()
            if len(daily_df) > 100:
                # Scoring
                try:
                    scored_df = scorer.apply_sector_scoring(daily_df, financials, consensus)
                    
                    if not scored_df.empty:
                        rank_map = dict(zip(scored_df['Ticker'], scored_df['Rank']))
                        price_map = dict(zip(scored_df['Ticker'], scored_df['Close']))
                        
                        # 1. Mark to Market & Sell
                        current_pf_value = cash
                        for t, p in portfolio.items():
                            if t in price_map:
                                current_pf_value += p['qty'] * price_map[t]
                        
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
                                trades.append({
                                    "date": date_str, "type": "SELL", "ticker": ticker,
                                    "price": price, "qty": qty, "proceeds": proceeds
                                })
                            del portfolio[ticker]
                        
                        # 2. Buy
                        open_slots = MAX_POSITIONS - len(portfolio)
                        if open_slots > 0:
                            # Recalculate value for sizing
                            curr_val_for_alloc = cash
                            for t, p in portfolio.items():
                                if t in price_map: curr_val_for_alloc += p['qty'] * price_map[t]
                                
                            target_alloc = curr_val_for_alloc / MAX_POSITIONS
                            
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
                                        trades.append({
                                            "date": date_str, "type": "BUY", "ticker": ticker,
                                            "price": price, "qty": qty, "cost": cost
                                        })
                except Exception as e:
                    # print(f"Error scoring {date_str}: {e}")
                    pass

        # --- C. Record History ---
        # Need daily value for chart
        # Get prices for all holdings (even if not rebalancing day)
        current_val = cash
        holdings_count = len(portfolio)
        
        # We need prices for holdings.
        # data_map has them.
        for ticker, pos in portfolio.items():
            if ticker in data_map:
                t_df = data_map[ticker]
                row = t_df[t_df['Date'] == date]
                if not row.empty:
                    current_val += pos['qty'] * row.iloc[0]['Close']
                else:
                    # Fallback to cost or previous
                    current_val += pos['cost'] # Rough approx if price missing today
            else:
                current_val += pos['cost']
                
        history.append({
            "date": date_str,
            "value": round(current_val, 2),
            "cash": round(cash, 2),
            "holdings": holdings_count,
            "total_div": round(total_dividends, 2)
        })

    # Results
    final_val = history[-1]['value']
    total_ret = (final_val - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100
    days = (datetime.strptime(history[-1]['date'], '%Y-%m-%d') - datetime.strptime(history[0]['date'], '%Y-%m-%d')).days
    cagr = ((final_val / INITIAL_CAPITAL) ** (365/days) - 1) * 100 if days > 0 else 0
    
    print("\n" + "="*50)
    print("📊 BACKTEST v3.0 RESULT (Dividend Reinvested)")
    print("="*50)
    print(f"💰 Final Value:    ${final_val:,.0f}")
    print(f"📈 Total Return:   {total_ret:.1f}%")
    print(f"💵 Total Dividends:{total_dividends:,.0f}")
    print(f"📅 CAGR:           {cagr:.1f}%")
    print("-" * 50)
    
    # Save & Sync
    # 1. Result JSON
    with open('backtest_v3_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            "metrics": {"Total_Return": total_ret, "Final_Value": final_val, "Total_Dividends": total_dividends},
            "history": history
        }, f, indent=2)
        
    # 2. Chart Data (with SPY Total Return)
    # We need SPY TR again to map
    print("🔄 Fetching SPY Total Return for comparison...")
    spy_df = yf.download('SPY', start=trading_days[0], end=datetime.now(), auto_adjust=True, progress=False)
    # spy_df might be MultiIndex
    if isinstance(spy_df.columns, pd.MultiIndex):
        spy_df = spy_df.xs('SPY', axis=1, level=0)
    
    chart_data = []
    for h in history:
        d = h['date']
        # SPY
        try:
            spy_val = spy_df.loc[d]['Close'].item()
        except:
            # Nearest
            try:
                idx = spy_df.index.get_indexer([pd.Timestamp(d)], method='nearest')[0]
                spy_val = spy_df.iloc[idx]['Close'].item()
            except:
                spy_val = 0
                
        chart_data.append({
            "date": d,
            "sb1": h['value'],
            "spy": spy_val
        })
        
    with open('data/chart_data.json', 'w', encoding='utf-8') as f:
        json.dump(chart_data, f, indent=2)
    print("✅ data/chart_data.json updated")
    
    # 3. Last State (Top 10 sync like before)
    # Actually we should just use the final cash/value and sync
    # Let's run sync_portfolio logic essentially here
    # Reuse previous logic: Allocate FINAL_VALUE to Top 10
    
    # But wait, user wanted "Continuity". 
    # If we update chart_data, we successfully show Dividend Reinvestment history.
    # We should also update portfolio_state to match this new higher value.
    
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
            "note": f"Synced with Backtest v3.0 (Div Reinvest) on {datetime.now().date()}"
        }
        with open('data/portfolio_state.json', 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
        print("✅ data/portfolio_state.json synced")
        
    except Exception as e:
        print(f"⚠️ State sync failed: {e}")

if __name__ == "__main__":
    run_backtest()
