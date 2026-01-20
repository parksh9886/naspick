import json
import pandas as pd
import yfinance as yf
from datetime import datetime

# Load existing chart data
print("📂 Loading chart_data.json...")
with open('data/chart_data.json', 'r', encoding='utf-8') as f:
    chart_data = json.load(f)

# Convert to DataFrame
df_chart = pd.DataFrame(chart_data)
df_chart['Date'] = pd.to_datetime(df_chart['date'])
df_chart.set_index('Date', inplace=True)

start_date = df_chart.index.min().strftime('%Y-%m-%d')
end_date = df_chart.index.max().strftime('%Y-%m-%d')
# Extend end_date slightly to ensure we capture the last day
end_date_fetch = (pd.to_datetime(end_date) + pd.Timedelta(days=2)).strftime('%Y-%m-%d')

print(f"📊 Fetching S&P 500 (SPY) Total Return data from {start_date} to {end_date}...")

# Use auto_adjust=True for Total Return (Dividend Reinvested)
# Suppress progress bar
df_spy = yf.download('SPY', start=start_date, end=end_date_fetch, auto_adjust=True, progress=False)

# Handle MultiIndex columns if present (yfinance update)
if isinstance(df_spy.columns, pd.MultiIndex):
    try:
        df_spy = df_spy.xs('SPY', axis=1, level=0)
    except:
        pass # Might be already flat or different structure

# Process
new_chart_data = []

print("🔄 Merging and formatting data...")
for date, row in df_chart.iterrows():
    date_str = date.strftime('%Y-%m-%d')
    
    # Get SPY price (Close is now Adj Close due to auto_adjust=True)
    try:
        # Use simple lookup if available
        # yfinance index is DatetimeIndex usually with timezone?
        # Normalize timezone if needed
        # Let's try matching string dates if direct lookup fails
        val = df_spy.loc[date]['Close']
        if isinstance(val, pd.Series): 
             val = val.item() # If duplicate index?
    except KeyError:
        # Nearest lookup
        try:
            timestamp = pd.Timestamp(date)
            # Find index with nearest date
            idx = df_spy.index.get_indexer([timestamp], method='nearest')[0]
            val = df_spy.iloc[idx]['Close']
        except:
             val = row.get('spy', 0) # Fallback to existing or 0

    # Ensure scalar
    if hasattr(val, 'item'):
        val = val.item()
        
    item = {
        "date": date_str,
        "sb1": row['sb1'],   # Keep sb1
        "spy": float(val)    # Update spy with Total Return
    }
    new_chart_data.append(item)

# Save
with open('data/chart_data.json', 'w', encoding='utf-8') as f:
    json.dump(new_chart_data, f, indent=2)

print("✅ chart_data.json repaired with Total Return (Adj Close) data.")
