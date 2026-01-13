import pandas as pd
import json
import os
import matplotlib.pyplot as plt

def load_ranks():
    print("📂 Loading ranking history...")
    if not os.path.exists('data/ranking_history.csv'):
        print("❌ ranking_history.csv not found!")
        return None
    
    df = pd.read_csv('data/ranking_history.csv', parse_dates=['Date'])
    # Sort by Date and Rank
    df = df.sort_values(['Date', 'Rank'])
    return df

def run_backtest(df):
    print("🧪 Running Backtest Simulation...")
    
    initial_capital = 100000
    cash = initial_capital
    portfolio = {} # {ticker: quantity}
    portfolio_history = []
    
    dates = df['Date'].unique()
    import numpy as np
    dates = np.sort(dates)
    
    trade_log = []
    
    FEE_RATE = 0.0025 # 0.25%

    for date in dates:
        # Get daily data
        daily_ranks = df[df['Date'] == date].set_index('Ticker')
        
        # 1. Update Portfolio Value (Mark to Market)
        current_equity = cash
        
        to_sell = []
        
        # Check holdings
        for ticker, qty in portfolio.items():
            if ticker in daily_ranks.index:
                price = daily_ranks.loc[ticker, 'Close']
                rank = daily_ranks.loc[ticker, 'Rank']
                
                current_equity += qty * price
                
                # Sell Condition: Rank > 20 or Rank is NaN (delisted from ranks)
                if rank > 20 or pd.isna(rank):
                    to_sell.append(ticker)
            else:
                # Ticker missing from data (suspended/delisted?) - Force Sell at last known?
                # For MVP, just keep holding or assume sold (Corner case)
                # Let's assume we sell if missing
                to_sell.append(ticker)
        
        # Execute Sells
        for ticker in to_sell:
            if ticker in daily_ranks.index:
                price = daily_ranks.loc[ticker, 'Close']
                rank = daily_ranks.loc[ticker, 'Rank']
            else:
                # Use last price from somewhere? 
                # This is tricky. Let's skip selling if missing for now or use 0? 
                # Simplified: Assume sell at 0 (Worst case) or just don't process.
                continue
                
            qty = portfolio[ticker]
            proceeds = qty * price * (1 - FEE_RATE)
            cash += proceeds
            del portfolio[ticker]
            
            trade_log.append({
                "Date": str(pd.to_datetime(date).date()),
                "Type": "SELL",
                "Ticker": ticker,
                "Price": price,
                "Rank": rank,
                "Qty": qty,
                "Balance": cash,
                "Fee": qty * price * FEE_RATE
            })
            
        # 2. Buy Logic
        # Target: Top 10
        # Max Stocks: 20
        # Allocation: Equal weight (1/20 of Total Equity? Or 1/20 of Initial?)
        # Let's use 1/20 of Current Total Equity Strategy (Rebalancing-ish) or Fixed Size?
        # Simple: 5% of Equity per stock.
        
        target_size = 20
        open_slots = target_size - len(portfolio)
        
        if open_slots > 0:
            # Look at Top 10 Ranks
            top_candidates = daily_ranks[daily_ranks['Rank'] <= 10].sort_values('Rank')
            
            for ticker, row in top_candidates.iterrows():
                if open_slots <= 0: break
                
                if ticker not in portfolio:
                    price = row['Close']
                    rank = row['Rank']
                    
                    # Position Sizing: 1/20 of CURRENT Equity
                    # But we don't want to use all cash if we already hold 19 stocks.
                    # Just allocate (Total Equity / 20) per trade.
                    
                    target_pos_value = current_equity / target_size
                    cost_basis = price * (1 + FEE_RATE)
                    
                    if cash > target_pos_value * 0.9: # Buffer
                        # Calculate qty based on target value including fee estimate
                        qty = int(target_pos_value / cost_basis)
                        
                        if qty > 0:
                            cost = qty * price * (1 + FEE_RATE)
                            cash -= cost
                            portfolio[ticker] = qty
                            open_slots -= 1
                            
                            trade_log.append({
                                "Date": str(pd.to_datetime(date).date()),
                                "Type": "BUY",
                                "Ticker": ticker,
                                "Price": price,
                                "Rank": rank,
                                "Qty": qty,
                                "Balance": cash, 
                                "Fee": qty * price * FEE_RATE
                            })
                            
        # Log End of Day State
        total_value = cash
        for t, q in portfolio.items():
            if t in daily_ranks.index:
                 total_value += q * daily_ranks.loc[t, 'Close']
        
        portfolio_history.append({
            "Date": date,
            "Total_Value": total_value,
            "Cash": cash,
            "Holdings": len(portfolio)
        })
        
    # Stats
    df_res = pd.DataFrame(portfolio_history)
    
    if df_res.empty:
        print("❌ Backtest failed to generate history")
        return

    final_val = df_res.iloc[-1]['Total_Value']
    total_r = (final_val - initial_capital) / initial_capital * 100
    
    # CAGR (approx)
    days = (df_res.iloc[-1]['Date'] - df_res.iloc[0]['Date']).days
    cagr = ((final_val / initial_capital) ** (365/days) - 1) * 100 if days > 0 else 0
    
    print("-" * 50)
    print(f"💰 Initial Capital: ${initial_capital:,.0f}")
    print(f"💰 Final Value:    ${final_val:,.0f}")
    print(f"📈 Total Return:   {total_r:.2f}%")
    print(f"📅 CAGR:           {cagr:.2f}%")
    print(f"🔄 Total Trades:   {len(trade_log)}")
    print("-" * 50)
    
    # Save Results
    results = {
        "metrics": {
            "Total_Return": total_r,
            "CAGR": cagr,
            "Final_Value": final_val
        },
        "history": json.loads(df_res.to_json(orient='records', date_format='iso')),
        "trades": trade_log
    }
    
    with open('backtest_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("✅ Saved backtest_results.json")

def main():
    df = load_ranks()
    if df is not None:
        run_backtest(df)

if __name__ == "__main__":
    main()
