import json

with open('data.json', encoding='utf-8') as f:
    data = json.load(f)

print(f"\n✅ Successfully loaded {len(data)} stocks!\n")
print("📊 Top 10 Rankings:")
print("-" * 50)
for i, stock in enumerate(data[:10], 1):
    print(f"{i:2d}. {stock['ticker']:6s} | Score: {stock['final_score']:5.1f} | ${stock['current_price']:8.2f} | {stock['change_pct']:+6.2f}%")

print(f"\n🎯 Tier distribution:")
tiers = {}
for stock in data:
    tier = stock['tier']
    tiers[tier] = tiers.get(tier, 0) + 1

for tier in sorted(tiers.keys()):
    print(f"   Tier {tier}: {tiers[tier]} stocks")
