import json

# Load data
with open('data/consensus_data.json', 'r', encoding='utf-8') as f:
    consensus = json.load(f)

with open('data/data.json', 'r', encoding='utf-8') as f:
    stocks = json.load(f)

# Financial sector stocks
banks = ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'BLK', 'SCHW', 'AXP', 'COF']

print("=" * 60)
print("금융주 부채비율 분석")
print("=" * 60)
for t in banks:
    cons = consensus.get(t, {})
    fh = cons.get('financial_health', {})
    debt = fh.get('debt_ratio', 'N/A')
    print(f"{t:5s}: 부채비율 = {debt}")

print("\n" + "=" * 60)
print("금융주 순위 (현재 data.json)")
print("=" * 60)
fin_stocks = [d for d in stocks if d.get('sector') == '금융']
fin_sorted = sorted(fin_stocks, key=lambda x: x['rank'])[:15]

for d in fin_sorted:
    print(f"Rank {d['rank']:3d} | {d['ticker']:5s} | Score: {d['final_score']:5.1f} | {d['name']}")

print("\n" + "=" * 60)
print("전체 TOP 20 순위")
print("=" * 60)
all_sorted = sorted(stocks, key=lambda x: x['rank'])[:20]
for d in all_sorted:
    sec = d.get('sector', 'N/A')
    print(f"Rank {d['rank']:3d} | {d['ticker']:5s} | Score: {d['final_score']:5.1f} | {sec:10s} | {d['name']}")
