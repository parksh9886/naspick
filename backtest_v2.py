"""
5-Year Backtest with New Scoring Logic (v2.0)
- Fetches 5 years of price data
- Recalculates scores daily using new scorer.py
- Simulates portfolio with TOP 10 buy, EXIT_RANK 20 sell rule
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import FinanceDataReader as fdr

from scripts.core.scorer import MarketScorer

# ===== CONFIG =====
INITIAL_CAPITAL = 100000
TOP_N = 10
EXIT_RANK = 20
MAX_POSITIONS = 20
FEE_RATE = 0.0025  # 0.25%
START_DATE = "2020-01-01"  # Fetch from early 2020 to have enough warmup for 2020-12-24 start

def load_financials():
    """Load financial data (assuming static for backtest)"""
    df = pd.read_csv('data/financials.csv')
    return df

def load_consensus():
    """Load consensus data"""
    with open('data/consensus_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def get_sp500_tickers():
    """Get S&P 500 ticker list"""
    try:
        df = fdr.StockListing('S&P500')
        return df['Symbol'].tolist()
    except:
        # Fallback
        with open('data/data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return [d['ticker'] for d in data]

def fetch_price_data(tickers, start_date, end_date):
    """Fetch historical price data for all tickers"""
    print(f"📈 Fetching price data: {start_date} to {end_date}")
    
    all_data = []
    for i, ticker in enumerate(tickers):
        if i % 50 == 0:
            print(f"   Progress: {i}/{len(tickers)}")
        try:
            df = fdr.DataReader(ticker, start_date, end_date)
            if df is not None and len(df) > 0:
                df = df.reset_index()
                df['Ticker'] = ticker
                # Rename 'index' to 'Date' if needed
                if 'index' in df.columns:
                    df = df.rename(columns={'index': 'Date'})
                # Select only the columns we need
                cols = ['Date', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Volume']
                df = df[[c for c in cols if c in df.columns]]
                all_data.append(df)
        except Exception as e:
            pass
    
    print(f"   Collected data from {len(all_data)} tickers")
    
    if not all_data:
        return pd.DataFrame()
    
    return pd.concat(all_data, ignore_index=True)

def run_backtest():
    print("=" * 60)
    print("🧪 Full Backtest with New Scoring Logic (v2.0)")
    print("   Starting from 2020-12-24")
    print("=" * 60)
    
    # Setup
    scorer = MarketScorer()
    financials = load_financials()
    consensus = load_consensus()
    
    end_date = datetime.now()
    start_date = datetime.strptime(START_DATE, '%Y-%m-%d')
    
    # Fetch tickers
    tickers = get_sp500_tickers()
    print(f"📋 Tickers: {len(tickers)}")
    
    # Fetch price data
    price_df = fetch_price_data(tickers, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    
    if price_df.empty:
        print("❌ No price data fetched!")
        return
    
    print(f"✓ Loaded {len(price_df)} price records")
    
    # Calculate technical factors (bulk)
    price_df = scorer.calculate_technical_factors_bulk(price_df)
    
    # Get unique trading days
    trading_days = sorted(price_df['Date'].unique())
    print(f"📅 Trading days: {len(trading_days)}")
    
    # Skip first 252 days (need history for momentum)
    trading_days = trading_days[252:]
    
    # Backtest simulation
    cash = INITIAL_CAPITAL
    portfolio = {}  # {ticker: {'qty': int, 'cost': float}}
    history = []
    trades = []
    
    # Weekly rebalancing (every 5 trading days)
    rebalance_days = trading_days[::5]
    print(f"📊 Rebalance dates: {len(rebalance_days)}")
    
    for i, date in enumerate(rebalance_days):
        if i % 50 == 0:
            print(f"   Simulating: {i}/{len(rebalance_days)} ({date.date()})")
        
        # Get daily data
        daily_df = price_df[price_df['Date'] == date].copy()
        
        if len(daily_df) < 100:  # Need enough stocks
            continue
        
        # Calculate scores
        try:
            scored_df = scorer.apply_sector_scoring(daily_df, financials, consensus)
        except Exception as e:
            continue
        
        if scored_df.empty:
            continue
        
        # Create rank map
        rank_map = dict(zip(scored_df['Ticker'], scored_df['Rank']))
        price_map = dict(zip(scored_df['Ticker'], scored_df['Close']))
        
        # 1. Mark to market
        total_value = cash
        for ticker, pos in portfolio.items():
            if ticker in price_map:
                total_value += pos['qty'] * price_map[ticker]
        
        # 2. Sell: Rank > EXIT_RANK
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
                    "date": str(date.date()),
                    "type": "SELL",
                    "ticker": ticker,
                    "price": price,
                    "qty": qty,
                    "proceeds": proceeds
                })
            del portfolio[ticker]
        
        # 3. Buy: Top N (if room)
        open_slots = MAX_POSITIONS - len(portfolio)
        if open_slots > 0:
            top_stocks = scored_df[scored_df['Rank'] <= TOP_N].sort_values('Rank')
            
            for _, row in top_stocks.iterrows():
                if open_slots <= 0:
                    break
                    
                ticker = row['Ticker']
                if ticker in portfolio:
                    continue
                
                price = row['Close']
                target_value = total_value / MAX_POSITIONS
                
                if cash > target_value * 0.9:
                    qty = int(target_value / (price * (1 + FEE_RATE)))
                    if qty > 0:
                        cost = qty * price * (1 + FEE_RATE)
                        cash -= cost
                        portfolio[ticker] = {'qty': qty, 'cost': cost}
                        open_slots -= 1
                        trades.append({
                            "date": str(date.date()),
                            "type": "BUY",
                            "ticker": ticker,
                            "price": price,
                            "qty": qty,
                            "cost": cost
                        })
        
        # 4. Record history
        total_value = cash
        for ticker, pos in portfolio.items():
            if ticker in price_map:
                total_value += pos['qty'] * price_map[ticker]
        
        history.append({
            "date": str(date.date()),
            "value": round(total_value, 2),
            "cash": round(cash, 2),
            "holdings": len(portfolio)
        })
    
    # Results
    if not history:
        print("❌ No history generated!")
        return
    
    final_value = history[-1]['value']
    total_return = (final_value - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100
    
    days = (datetime.strptime(history[-1]['date'], '%Y-%m-%d') - 
            datetime.strptime(history[0]['date'], '%Y-%m-%d')).days
    cagr = ((final_value / INITIAL_CAPITAL) ** (365/days) - 1) * 100 if days > 0 else 0
    
    print("\n" + "=" * 60)
    print("📊 BACKTEST RESULTS")
    print("=" * 60)
    print(f"💰 Initial Capital: ${INITIAL_CAPITAL:,.0f}")
    print(f"💰 Final Value:     ${final_value:,.0f}")
    print(f"📈 Total Return:    {total_return:.1f}%")
    print(f"📅 CAGR:            {cagr:.1f}%")
    print(f"🔄 Total Trades:    {len(trades)}")
    print(f"📅 Period:          {history[0]['date']} to {history[-1]['date']}")
    
    # Save results
    results = {
        "metrics": {
            "initial_capital": INITIAL_CAPITAL,
            "final_value": final_value,
            "total_return": round(total_return, 2),
            "cagr": round(cagr, 2),
            "total_trades": len(trades),
            "period": f"{history[0]['date']} to {history[-1]['date']}"
        },
        "history": history,
        "trades": trades[-50:]  # Last 50 trades only
    }
    
    with open('backtest_v2_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print("\n✅ Saved backtest_v2_results.json")
    
    # Update chart_data.json for website
    chart_data = [{"date": h['date'], "value": h['value']} for h in history]
    with open('data/chart_data.json', 'w', encoding='utf-8') as f:
        json.dump(chart_data, f, indent=2)
    
    print("✅ Updated data/chart_data.json")

if __name__ == "__main__":
    run_backtest()
