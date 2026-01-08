import json
import os
from datetime import datetime

def main():
    print(f"📸 Taking Daily Snapshot of Ranks... ({datetime.now()})")
    
    if not os.path.exists('data.json'):
        print("❌ data.json not found!")
        return

    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create snapshot: Ticker -> {rank, sector_rank}
    # Note: data.json might not have 'sector_rank' yet if fetch_sp500 hasn't been updated.
    # So we might need to compute it here or ensure fetch_sp500 runs first.
    # Assuming fetch_sp500.py is updated to include sector_rank, or we calculate it here.
    
    # Let's calculate sector ranks here just in case, ensuring consistency.
    # But wait, fetch_sp500.py will do the heavy lifting of sorting.
    # Let's rely on data.json having correct 'rank'. For 'sector_rank', let's derive it to be safe.
    
    # 1. Group by sector
    by_sector = {}
    for item in data:
        sec = item.get('sector', 'Unknown')
        if sec not in by_sector:
            by_sector[sec] = []
        by_sector[sec].append(item)
    
    # 2. Sort and assign sector ranks based on final_score
    sector_ranks_map = {}
    for sec, items in by_sector.items():
        # Sort desc by score
        items.sort(key=lambda x: x.get('final_score', 0), reverse=True)
        for idx, item in enumerate(items):
            sector_ranks_map[item['ticker']] = idx + 1
            
    snapshot = {}
    for item in data:
        snapshot[item['ticker']] = {
            "rank": item.get('rank', 9999),
            "sector_rank": sector_ranks_map.get(item['ticker'], 9999)
        }
        
    with open('yesterday_ranks.json', 'w', encoding='utf-8') as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)
        
    print(f"✅ Saved snapshot for {len(snapshot)} tickers to yesterday_ranks.json")

if __name__ == "__main__":
    main()
