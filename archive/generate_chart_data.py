
import pandas as pd
import json
import numpy as np
from multi_backtest import load_data, run_strategy_simulation, STRATEGIES, get_benchmark

def main():
    print("📊 Generating Chart Data (SB1 vs SPY)...")
    
    # 1. Load Data
    df = load_data()
    if df is None: return

    # 2. Run SB1 Simulation (Full History)
    print("   Running SB1 Simulation...")
    res_sb1, _ = run_strategy_simulation(df, 'SB1', STRATEGIES['SB1'], fee_rate=0.0)
    
    # 3. Get Benchmark (SPY)
    print("   Fetching S&P 500 Benchmark...")
    start_date = res_sb1.index[0]
    end_date = res_sb1.index[-1]
    spy_data = get_benchmark(start_date, end_date)
    
    # 4. Normalize and Combine
    res_sb1 = res_sb1.rename(columns={'Value': 'SB1'})
    
    combined = res_sb1[['SB1']].copy()
    
    if spy_data is not None:
        spy_vals = spy_data.reindex(combined.index, method='ffill')['Benchmark_Value']
        # Normalize SPY start to match SB1 start (100k)
        start_val = spy_vals.iloc[0]
        factor = 100000 / start_val
        combined['SPY'] = spy_vals * factor
    else:
        combined['SPY'] = 0
        
    # 5. Format for Frontend (JSON: [{date, sb1, spy}, ...])
    chart_data = []
    for date, row in combined.iterrows():
        chart_data.append({
            "date": date.strftime('%Y-%m-%d'),
            "sb1": round(row['SB1'], 2),
            "spy": round(row['SPY'], 2)
        })
        
    # Save
    with open('chart_data.json', 'w') as f:
        json.dump(chart_data, f)
        
    print(f"✅ Saved {len(chart_data)} points to chart_data.json")

if __name__ == "__main__":
    main()
