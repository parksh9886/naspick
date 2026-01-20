import json

# Load current data (after new scoring logic)
with open('data/data.json', 'r', encoding='utf-8') as f:
    stocks = json.load(f)

# Financial sector analysis
fin_stocks = [s for s in stocks if s.get('sector') == '금융']
fin_sorted = sorted(fin_stocks, key=lambda x: x['rank'])[:10]

print("=" * 70)
print("금융주 TOP 10 - score_breakdown 분석")
print("=" * 70)

for s in fin_sorted:
    sb = s.get('score_breakdown', {})
    stats = s.get('stats_bar', {})
    print(f"\n{s['rank']:2d}위 | {s['ticker']:5s} | 총점: {s['final_score']:.1f}")
    if sb:
        print(f"  Value: {sb.get('value', 0):.1f}/20 | Growth: {sb.get('growth', 0):.1f}/20 | Profit: {sb.get('profitability', 0):.1f}/15")
        print(f"  Momentum: {sb.get('momentum', 0):.1f}/20 | Stability: {sb.get('stability', 0):.1f}/5 | Risk: {sb.get('risk', 0):.1f}/5")
        print(f"  Consensus: {sb.get('consensus', 0):.1f}/10 | Sentiment: {sb.get('sentiment', 0):.1f}/5")
    else:
        print(f"  stats_bar: {stats}")

# Compare tech vs financial
print("\n" + "=" * 70)
print("기술 vs 금융 평균 score_breakdown 비교")
print("=" * 70)

tech_stocks = [s for s in stocks if s.get('sector') == '기술']

def avg_breakdown(stock_list):
    factors = ['value', 'growth', 'profitability', 'momentum', 'stability', 'risk', 'consensus', 'sentiment']
    avgs = {}
    for f in factors:
        vals = [s.get('score_breakdown', {}).get(f, 0) for s in stock_list]
        avgs[f] = sum(vals) / len(vals) if vals else 0
    return avgs

fin_avg = avg_breakdown(fin_stocks)
tech_avg = avg_breakdown(tech_stocks)

print(f"\n{'Factor':<15} | {'금융 평균':>10} | {'기술 평균':>10} | {'차이':>8}")
print("-" * 50)
for f in ['value', 'growth', 'profitability', 'momentum', 'stability', 'risk', 'consensus', 'sentiment']:
    diff = fin_avg[f] - tech_avg[f]
    winner = "금융↑" if diff > 0.5 else ("기술↑" if diff < -0.5 else "비슷")
    print(f"{f:<15} | {fin_avg[f]:>10.2f} | {tech_avg[f]:>10.2f} | {winner:>8}")
