
import pandas as pd
import numpy as np
from multi_backtest import STRATEGIES, run_strategy_simulation, load_data

def main():
    print("📜 Generating Full 5-Year Trade Log (SB1)...")
    df = load_data()
    if df is None: return
    
    # Run from Entry (2021-01)
    res, trades, logs = run_strategy_simulation(df, 'SB1', STRATEGIES['SB1'], fee_rate=0.0025, return_trade_log=True)
    
    final_val = res['Value'].iloc[-1]
    ret = (final_val - 100000) / 1000
    
    print(f"\n==== 💎 Official Trade Log (2021-2025) ====")
    print(f"Total Return: +{ret:.1f}% | Final Value: ${final_val:,.0f}")
    print(f"{'Date':<12} {'Action':<6} {'Ticker':<8} {'Price':<10} {'Qty':<5}")
    print("-" * 50)
    
    # Verify log format
    for log in logs:
        # Format Date
        d = log['Date']
        # check if action is BUY/SELL
        print(f"{d:<12} {log['Action']:<6} {log['Ticker']:<8} ${log['Price']:<9.2f} {log['Qty']:<5}")
        
    # Save to CSV for User
    pd.DataFrame(logs).to_csv('sb1_full_trade_log.csv', index=False)
    print("\n✅ Saved to sb1_full_trade_log.csv")

if __name__ == "__main__":
    main()
