import json
import pandas as pd
import FinanceDataReader as fdr
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

print(f"📊 Fetching S&P 500 (SPY) data from {start_date} to {end_date}...")
df_spy = fdr.DataReader('SPY', start_date, end_date)

# Process
new_chart_data = []

print("🔄 Merging and formatting data...")
for date, row in df_chart.iterrows():
    date_str = date.strftime('%Y-%m-%d')
    
    # Get SPY price (Close)
    # Find closest date if exact match missing (e.g. holidays differ?)
    # But usually just reindexing is better. Simple lookup for now.
    try:
        spy_val = df_spy.loc[date]['Close']
    except KeyError:
        # Try finding nearest previous date
        # (Simplified: just use prev value or skip?)
        # Let's use asof behavior if using pandas properly, 
        # but here just get from index lookup
        idx = df_spy.index.get_indexer([date], method='nearest')[0]
        spy_val = df_spy.iloc[idx]['Close']

    item = {
        "date": date_str,
        "sb1": row['value'],   # Rename value -> sb1
        "spy": float(spy_val)  # Add spy
    }
    new_chart_data.append(item)

# Save
with open('data/chart_data.json', 'w', encoding='utf-8') as f:
    json.dump(new_chart_data, f, indent=2)

print("✅ chart_data.json repaired with 'sb1' and 'spy' keys.")
