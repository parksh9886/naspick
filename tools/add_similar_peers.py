import json

# Load data
with open('data/data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Sort by rank
data.sort(key=lambda x: x['rank'])
total_count = len(data)

# Add similar_score_peers
for item in data:
    current_rank = item['rank']
    current_idx = current_rank - 1
    
    if current_rank == 1:
        indices = [1, 2, 3]
    elif current_rank == 2:
        indices = [0, 2, 3]
    elif current_rank >= total_count - 1:
        indices = [current_idx - 3, current_idx - 2, current_idx - 1]
    else:
        indices = [current_idx - 2, current_idx - 1, current_idx + 1]
    
    similar_peers = []
    for idx in indices:
        if 0 <= idx < total_count and idx != current_idx:
            p = data[idx]
            similar_peers.append({'ticker': p['ticker'], 'change_pct': p['change_pct']})
    
    item['similar_score_peers'] = similar_peers[:3]

# Save
with open('data/data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f'Added similar_score_peers to {total_count} stocks')
print(f'Sample (1st): {data[0]["ticker"]} -> {data[0]["similar_score_peers"]}')
print(f'Sample (2nd): {data[1]["ticker"]} -> {data[1]["similar_score_peers"]}')
print(f'Sample (Last): {data[-1]["ticker"]} -> {data[-1]["similar_score_peers"]}')
