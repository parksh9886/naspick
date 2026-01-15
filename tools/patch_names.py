import json
from sp500_korean_names import SP500_KOREAN_NAMES

try:
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    updated_count = 0
    for item in data:
        ticker = item['ticker']
        # Check if we have a Korean name for this ticker
        if ticker in SP500_KOREAN_NAMES:
            current_name = item['name']
            new_name = SP500_KOREAN_NAMES[ticker]
            
            # If current name is just ticker or different from new mapping
            if current_name != new_name:
                print(f"Updating {ticker}: {current_name} -> {new_name}")
                item['name'] = new_name
                updated_count += 1
                
    if updated_count > 0:
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"SUCCESS: Updated {updated_count} names in data.json")
    else:
        print("No updates needed.")

except Exception as e:
    print(f"Error: {e}")
