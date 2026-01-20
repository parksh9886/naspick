
import pandas as pd
import glob
import os

try:
    # 1. Read ALL CSV files and combine them
    list_of_files = glob.glob(r'c:\Users\sec\Desktop\Naspick\Keyword\*.csv')
    if not list_of_files:
        print("No CSV files found.")
        exit()
    
    print(f"Found {len(list_of_files)} CSV files. Reading all...")
    
    dfs = []
    for f in list_of_files:
        try:
            df_temp = pd.read_csv(f, encoding='utf-16', sep='\t', skiprows=2)
            dfs.append(df_temp)
        except Exception as e:
            print(f"  Error reading {os.path.basename(f)}: {e}")
    
    if not dfs:
        print("No data loaded.")
        exit()
        
    df = pd.concat(dfs, ignore_index=True)
    # Drop duplicates (same keyword might be in multiple files)
    df = df.drop_duplicates(subset=['Keyword'])
    
    print(f"Total unique keywords: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    
    # 2. Find Column Names (Korean or English headers)
    vol_col = 'Avg. monthly searches'
    comp_col = 'Competition'
    comp_idx_col = 'Competition (indexed value)'
    bid_col = 'Top of page bid (high range)'
    
    # 3. Clean Data
    df[vol_col] = pd.to_numeric(df[vol_col], errors='coerce').fillna(0).astype(int)
    df[comp_idx_col] = pd.to_numeric(df[comp_idx_col], errors='coerce').fillna(100)
    # Clean bid column (remove $ and convert to float)
    if bid_col in df.columns:
        df[bid_col] = df[bid_col].replace('[\$,]', '', regex=True)
        df[bid_col] = pd.to_numeric(df[bid_col], errors='coerce').fillna(0)
    
    # 4. Filter: Volume > 500, Competition is '낮음' or '보통' or indexed < 50, Bid > 0
    # GOLDEN KEYWORD CRITERIA:
    #   - High Volume (> 500)
    #   - Low Competition (낮음 or indexed < 35)
    #   - Has CPC (Bid > 0)
    
    print("\n" + "="*80)
    print("🏆 GOLDEN KEYWORDS (High Volume, Low Comp, Has CPC)")
    print("="*80)
    
    df_gold = df[
        (df[vol_col] >= 500) & 
        ((df[comp_col] == '낮음') | (df[comp_idx_col] <= 35)) &
        (df[bid_col] > 0)
    ].copy()
    
    # Sort by Volume descending
    df_gold = df_gold.sort_values(by=vol_col, ascending=False)
    
    print(f"{'Keyword':<40} | {'Volume':<8} | {'Comp':<6} | {'CPC':>8}")
    print("-" * 70)
    for _, row in df_gold.head(30).iterrows():
        kw = str(row['Keyword'])[:40]
        vol = int(row[vol_col])
        comp = str(row[comp_col])
        bid = row[bid_col]
        print(f"{kw:<40} | {vol:<8} | {comp:<6} | ${bid:>7.2f}")
    
    # 5. SILVER KEYWORDS (High Volume, Low Comp, NO CPC but still valuable)
    print("\n" + "="*80)
    print("🥈 SILVER KEYWORDS (High Volume, Low Comp, No CPC)")
    print("="*80)
    
    df_silver = df[
        (df[vol_col] >= 1000) & 
        ((df[comp_col] == '낮음') | (df[comp_idx_col] <= 35)) &
        (df[bid_col] == 0)
    ].copy().sort_values(by=vol_col, ascending=False)
    
    print(f"{'Keyword':<40} | {'Volume':<8} | {'Comp':<6}")
    print("-" * 60)
    for _, row in df_silver.head(20).iterrows():
        kw = str(row['Keyword'])[:40]
        vol = int(row[vol_col])
        comp = str(row[comp_col])
        print(f"{kw:<40} | {vol:<8} | {comp:<6}")
        
    # 6. MUST-RANK PATTERNS (Keywords you MUST win)
    print("\n" + "="*80)
    print("🎯 KEY PATTERNS TO TARGET (Based on Keywords Found)")
    print("="*80)
    
    patterns = ['적정 주가', '목표 주가', '주가 전망', '배당', 'AI', '티어', '등급', 'RSI', '저평가']
    for pat in patterns:
        subset = df[df['Keyword'].str.contains(pat, case=False, na=False)]
        if not subset.empty:
            top_kw = subset.sort_values(by=vol_col, ascending=False).iloc[0]
            print(f"  Pattern '{pat}': Top is '{top_kw['Keyword']}' with {int(top_kw[vol_col])} searches")

except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Error: {e}")
