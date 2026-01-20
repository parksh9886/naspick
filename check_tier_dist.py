import json
import pandas as pd

# Load data
with open('data/data.json', 'r', encoding='utf-8') as f:
    stocks = json.load(f)

# Tier 1 분석 (상위 5%)
tier1_count = len([s for s in stocks if s.get('tier') == 1])
print(f"전체 Tier 1 종목 수: {tier1_count}")

# 섹터별 Tier 1 분포
sectors = {}
for s in stocks:
    sec = s.get('sector', 'Unknown')
    if sec not in sectors:
        sectors[sec] = {'total': 0, 'tier1': 0}
    sectors[sec]['total'] += 1
    if s.get('tier') == 1:
        sectors[sec]['tier1'] += 1

print("\n" + "=" * 60)
print("섹터별 Tier 1 분포")
print("=" * 60)
for sec, data in sorted(sectors.items(), key=lambda x: x[1]['tier1'], reverse=True):
    pct = data['tier1'] / data['total'] * 100 if data['total'] > 0 else 0
    print(f"{sec:15s}: {data['tier1']:2d} / {data['total']:3d} ({pct:5.1f}%)")

# 금융 섹터 stats_bar 분석
print("\n" + "=" * 60)
print("금융주 TOP 5 상세 분석")
print("=" * 60)
fin_stocks = [d for d in stocks if d.get('sector') == '금융']
fin_sorted = sorted(fin_stocks, key=lambda x: x['rank'])[:5]

for d in fin_sorted:
    stats = d.get('stats_bar', {})
    print(f"\n{d['ticker']} ({d['name']}) - Rank {d['rank']}, Score {d['final_score']}")
    print(f"  Trend: {stats.get('trend', 'N/A')}%")
    print(f"  Volume: {stats.get('volume', 'N/A')}%")
    print(f"  Momentum: {stats.get('momentum', 'N/A')}%")
    print(f"  Impact: {stats.get('impact', 'N/A')}%")
