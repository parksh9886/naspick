import json

try:
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    count = len(data)
    print(f"Total items: {count}")
    
    tickers = set(item['ticker'] for item in data)
    
    required = ['BRK.B', 'BF.B', 'GOOG', 'GOOGL', 'FOX', 'FOXA', 'NWS', 'NWSA']
    missing = [t for t in required if t not in tickers]
    
    if missing:
        print(f"FAILED: Missing tickers: {missing}")
        exit(1)
    else:
        print("SUCCESS: All required dual-class/special tickers present.")
        
    if count < 500:
        print("FAILED: Count less than 500")
        exit(1)
        
    print("Verification passed.")
    
except Exception as e:
    print(f"Error: {e}")
    exit(1)
