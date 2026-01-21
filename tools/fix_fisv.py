import json

with open('data/data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Get financials sector stocks (excluding FISV)
financials = [d for d in data if d['sector'] == '금융' and d['ticker'] != 'FISV']
financials.sort(key=lambda x: x['rank'])

# Update FISV related_peers with top 3 financials
for item in data:
    if item['ticker'] == 'FISV':
        item['related_peers'] = [{'ticker': p['ticker'], 'change_pct': p['change_pct']} for p in financials[:3]]
        peers = item['related_peers']
        print(f'Updated FISV related_peers: {peers}')
        break

with open('data/data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print('Done!')
