import json
import pandas as pd
import yfinance as yf
from datetime import datetime

# Load results
print("📂 Loading backtest results...")
with open('backtest_v3_results.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

history = results['history']
final_val = results['metrics']['Final_Value']
total_div = results['metrics']['Total_Dividends']
total_ret = results['metrics']['Total_Return']

print(f"📊 Backtest Loaded: Val=${final_val:,.0f}, Div=${total_div:,.0f}, Ret={total_ret:.1f}%")

# Fetch SPY
print("🔄 Fetching SPY Total Return...")
start_date = history[0]['date']
end_date = datetime.now().strftime('%Y-%m-%d')
spy_df = yf.download('SPY', start=start_date, end=end_date, auto_adjust=True, progress=False)

# Robust SPY handling
if isinstance(spy_df.columns, pd.MultiIndex):
    try:
        spy_df = spy_df.xs('SPY', axis=1, level=0)
    except:
        # Fallback: maybe just take first level?
        spy_df.columns = spy_df.columns.droplevel(1)

chart_data = []
for h in history:
    d = h['date']
    try:
        ts = pd.Timestamp(d)
        if ts in spy_df.index:
            spy_val = spy_df.loc[ts]['Close']
        else:
            idx = spy_df.index.get_indexer([ts], method='nearest')[0]
            spy_val = spy_df.iloc[idx]['Close']
            
        if hasattr(spy_val, 'item'): spy_val = spy_val.item()
    except Exception as e:
        spy_val = 0
        
    chart_data.append({
        "date": d,
        "sb1": h['value'],
        "spy": float(spy_val)
    })

with open('data/chart_data.json', 'w', encoding='utf-8') as f:
    json.dump(chart_data, f, indent=2)
print("✅ data/chart_data.json updated")

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
