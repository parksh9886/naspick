
import json

def update_tiers():
    print("🔄 Updating Tiers (Adding OP Tier)...")
    
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Re-calculate tiers based on rank
        # We need to sort by rank just in case, though they should be sorted.
        data.sort(key=lambda x: x['rank'])
        
        total = len(data)
        
        for i, item in enumerate(data):
            rank = i + 1
            pct = rank / total
            
            if pct <= 0.01: item['tier'] = "OP"
            elif pct <= 0.05: item['tier'] = 1
            elif pct <= 0.20: item['tier'] = 2
            elif pct <= 0.50: item['tier'] = 3
            elif pct <= 0.80: item['tier'] = 4
            else: item['tier'] = 5
            
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"✅ Updated {total} items. Top 1% is now OP Tier.")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    update_tiers()
