import json

with open('data/data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

fisv = next((d for d in data if d['ticker'] == 'FISV'), None)
if fisv:
    print(f"FISV found:")
    print(f"  sector: {fisv.get('sector')}")
    print(f"  rank: {fisv.get('rank')}")
    print(f"  final_score: {fisv.get('final_score')}")
    print(f"  related_peers: {fisv.get('related_peers')}")
    print(f"  similar_score_peers: {fisv.get('similar_score_peers')}")
else:
    print("FISV not found in data.json")
