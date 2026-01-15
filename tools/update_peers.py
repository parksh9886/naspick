import json

def update_peers():
    print("🚀 Updating Related Peers based on corrected sectors...")
    
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ data.json not found")
        return

    # Group by sector
    # Sort data by score first to ensure we pick top peers
    # Assuming final_score is present
    data.sort(key=lambda x: x.get('final_score', 0), reverse=True)
    
    sector_stocks = {}
    for item in data:
        sec = item.get('sector', 'Unknown')
        if sec not in sector_stocks:
            sector_stocks[sec] = []
        sector_stocks[sec].append(item)
    
    # Re-assign peers
    updated_count = 0
    for item in data:
        sec = item.get('sector', 'Unknown')
        # Get top 3 peers from same sector, excluding self
        peers = [p for p in sector_stocks.get(sec, []) if p['ticker'] != item['ticker']][:3]
        
        item['related_peers'] = [
            {"ticker": p['ticker'], "change_pct": p.get('change_pct', 0)} for p in peers
        ]
        updated_count += 1

    # Save
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Updated peer lists for {updated_count} stocks.")

if __name__ == "__main__":
    update_peers()
