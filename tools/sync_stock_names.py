"""
Stock Name Synchronizer
Fetches latest S&P 500 company names from Wikipedia (English & Korean)
and updates the name dictionaries automatically.
"""
import pandas as pd
import os
import io
import requests

def sync_stock_names():
    print("🔄 Syncing stock names from Wikipedia...")
    
    # Headers to avoid 403 Forbidden
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # 1. Fetch English names from Wikipedia
    print("   Fetching English names...")
    url_en = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    try:
        response = requests.get(url_en, headers=headers, timeout=30)
        response.raise_for_status()
        tables = pd.read_html(io.StringIO(response.text))
        df_en = tables[0]
        # Columns: Symbol, Security, GICS Sector, ...
        english_names = {}
        for _, row in df_en.iterrows():
            ticker = str(row['Symbol']).strip()
            name = str(row['Security']).strip()
            if ticker and name:
                # Clean ticker (BRK.B format)
                english_names[ticker] = name
        print(f"   ✓ Found {len(english_names)} English names")
    except Exception as e:
        print(f"   ❌ Failed to fetch English names: {e}")
        english_names = {}
    
    # 2. Fetch Korean names from Wikipedia
    print("   Fetching Korean names...")
    url_ko = "https://ko.wikipedia.org/wiki/S%26P_500"
    korean_names = {}
    try:
        response = requests.get(url_ko, headers=headers, timeout=30)
        response.raise_for_status()
        tables = pd.read_html(io.StringIO(response.text))
        # Korean Wikipedia table structure varies, try to find the right one
        for table in tables:
            if len(table) > 100:  # S&P 500 table should have many rows
                # Look for columns that might contain ticker and name
                cols = table.columns.tolist()
                for i, col in enumerate(cols):
                    if '티커' in str(col) or 'Symbol' in str(col) or '종목' in str(col):
                        ticker_col = col
                        # Name is usually next column or look for 회사 or 기업
                        for j, c in enumerate(cols):
                            if '회사' in str(c) or '기업' in str(c) or '이름' in str(c) or j == i + 1:
                                name_col = c
                                for _, row in table.iterrows():
                                    ticker = str(row[ticker_col]).strip()
                                    name = str(row[name_col]).strip()
                                    if ticker and name and ticker != 'nan':
                                        korean_names[ticker] = name
                                break
                        break
        print(f"   ✓ Found {len(korean_names)} Korean names from Wikipedia")
    except Exception as e:
        print(f"   ⚠️ Korean Wikipedia fetch failed: {e}")
    
    # 3. Load existing dictionaries
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    en_path = os.path.join(project_root, 'scripts', 'data', 'sp500_english_names.py')
    ko_path = os.path.join(project_root, 'scripts', 'data', 'sp500_korean_names.py')
    
    # Load existing English names
    existing_en = {}
    try:
        with open(en_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Extract dict using exec
            exec(content, {}, existing_en)
            existing_en = existing_en.get('SP500_ENGLISH_NAMES', {})
    except:
        pass
    
    # Load existing Korean names
    existing_ko = {}
    try:
        with open(ko_path, 'r', encoding='utf-8') as f:
            content = f.read()
            exec(content, {}, existing_ko)
            existing_ko = existing_ko.get('SP500_KOREAN_NAMES', {})
    except:
        pass
    
    # 4. Merge (keep existing, add new)
    new_en_count = 0
    new_ko_count = 0
    
    for ticker, name in english_names.items():
        if ticker not in existing_en:
            existing_en[ticker] = name
            new_en_count += 1
            print(f"   + New EN: {ticker} = {name}")
    
    for ticker, name in korean_names.items():
        if ticker not in existing_ko:
            existing_ko[ticker] = name
            new_ko_count += 1
            print(f"   + New KO: {ticker} = {name}")
    
    # For tickers with English name but no Korean name, use English
    for ticker in existing_en:
        if ticker not in existing_ko:
            existing_ko[ticker] = existing_en[ticker]
    
    # 5. Save updated dictionaries
    def save_dict(path, var_name, data):
        lines = [f"# S&P 500 Complete {var_name.replace('SP500_', '').replace('_', ' ').title()}"]
        lines.append(f"{var_name} = {{")
        
        # Sort by ticker
        sorted_items = sorted(data.items())
        for i, (k, v) in enumerate(sorted_items):
            # Escape quotes in value
            v_escaped = v.replace('"', '\\"').replace("'", "\\'")
            comma = "," if i < len(sorted_items) - 1 else ""
            lines.append(f'    "{k}": "{v_escaped}"{comma}')
        
        lines.append("}")
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')
    
    save_dict(en_path, 'SP500_ENGLISH_NAMES', existing_en)
    save_dict(ko_path, 'SP500_KOREAN_NAMES', existing_ko)
    
    print(f"\n✅ Sync complete!")
    print(f"   English: {len(existing_en)} total ({new_en_count} new)")
    print(f"   Korean: {len(existing_ko)} total ({new_ko_count} new)")
    
    return new_en_count + new_ko_count  # Return count of new names for git commit check

if __name__ == "__main__":
    sync_stock_names()
