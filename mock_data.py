import json
import random
from tickers import get_all_tickers
from stock_names import get_name

OUTPUT_FILE = "data.json"

SECTORS = [
    "기술", "커뮤니케이션", "임의소비재", "필수소비재", "에너지", 
    "금융", "헬스케어", "산업재", "소재", "부동산", "유틸리티"
]

def generate_mock_data():
    tickers = get_all_tickers()
    results = []
    
    for t in tickers:
        names = get_name(t)
        current_price = round(random.uniform(50, 2000), 2)
        change_pct = round(random.normalvariate(0.5, 2.0), 2)
        
        # Generated Scores
        base = random.choice([40, 50, 60, 70, 80])
        bonus = round(random.uniform(0, 20), 1)
        final = min(100.0, base + bonus)
        
        # Stats
        stats = {
            "trend": random.randint(50, 100),
            "volume": random.randint(20, 100),
            "momentum": random.randint(30, 90),
            "impact": random.randint(10, 90)
        }
        
        signals = []
        if stats['momentum'] > 80: signals.append("RSI_Overbought")
        if stats['trend'] > 90: signals.append("MACD_GoldenCross")

        # Support & Resistance (Pivot Points)
        # Mocking Previous Day Data
        prev_close = current_price
        prev_high = prev_close * random.uniform(1.01, 1.05)
        prev_low = prev_close * random.uniform(0.95, 0.99)
        
        pivot = (prev_high + prev_low + prev_close) / 3
        r1 = (2 * pivot) - prev_low
        r2 = pivot + (prev_high - prev_low)
        s1 = (2 * pivot) - prev_high
        s2 = pivot - (prev_high - prev_low)

        levels = {
            "pivot": round(pivot, 2),
            "r1": round(r1, 2),
            "r2": round(r2, 2),
            "s1": round(s1, 2),
            "s2": round(s2, 2)
        }

        # AI Briefing Generation (Mock Logic based on briefing_logic.txt)
        briefing = []
        
        # Slot 1: Trend
        if stats['trend'] >= 80:
            briefing.append({
                "id": 1,
                "title": "강력한 정배열",
                "text": "모든 이동평균선(20, 60, 100) 위에 주가가 위치하며 이상적인 상승 추세를 그리고 있음.",
                "color_class": "text-blue-400"
            })
        elif stats['trend'] >= 50:
             briefing.append({
                "id": 1,
                "title": "추세 전환 시도",
                "text": "단기 하락세를 멈추고 20일 이평선을 돌파하며 의미 있는 반등 시그널 발생.",
                "color_class": "text-[#00bba3]"
            })
        else:
             briefing.append({
                "id": 1,
                "title": "조정 국면",
                "text": "주요 지지선을 이탈하여 약세가 지속 중. 보수적인 접근이 필요함.",
                "color_class": "text-gray-400"
            })

        # Slot 2: Volume
        if stats['volume'] >= 80:
            briefing.append({
                "id": 2,
                "title": "수급 집중",
                "text": "평소 대비 2배 이상의 거래량이 터지며 메이저 주체(기관/외인)의 개입이 강력하게 의심됨.",
                "color_class": "text-[#00bba3]"
            })
        elif stats['volume'] <= 40:
             briefing.append({
                "id": 2,
                "title": "거래량 소강",
                "text": "상승 탄력이 둔화되며 거래량이 감소 중. 방향성 탐색 구간.",
                "color_class": "text-gray-400"
            })
        else:
             briefing.append({
                "id": 2,
                "title": "견조한 수급",
                "text": "특이 사항 없이 꾸준한 거래량을 동반하며 추세를 뒷받침하고 있음.",
                "color_class": "text-blue-400"
            })

        # Slot 3: Risk/Strategy
        simulated_rsi = stats['momentum']  # Use momentum as RSI proxy
        if simulated_rsi >= 70:
            briefing.append({
                "id": 3,
                "title": "과열 주의",
                "text": f"RSI {simulated_rsi}로 과매수 구간 진입. 신규 진입자는 눌림목(${levels['s1']})을 기다리는 것이 유리함.",
                "color_class": "text-rose-400"
            })
        elif simulated_rsi <= 30:
             briefing.append({
                "id": 3,
                "title": "기술적 반등 기대",
                "text": "RSI 침체권 진입. 단기 낙폭 과대로 인한 기술적 반등이 기대되는 구간.",
                "color_class": "text-blue-400"
            })
        else:
             briefing.append({
                "id": 3,
                "title": "홀딩 전략",
                "text": f"현재 추세가 유효하므로 1차 지지선(${levels['s1']}) 이탈 전까지는 추세 추종 전략 권장.",
                "color_class": "text-gray-400"
            })

        results.append({
            "ticker": t,
            "name": names['name'],
            "name_en": names['name_en'],
            "sector": random.choice(SECTORS),
            "current_price": current_price,
            "change_pct": change_pct,
            "market_cap": random.uniform(1e9, 2e12),
            "base_score": base,
            "bonus_score": bonus,
            "final_score": round(final, 1),
            "stats_bar": stats,
            "signals": signals,
            "levels": levels,
            "ai_briefing": briefing
        })

    # Sort & Tier
    results.sort(key=lambda x: x['final_score'], reverse=True)
    total = len(results)
    
    for idx, item in enumerate(results):
        rank_pct = (idx + 1) / total
        if rank_pct <= 0.05: item['tier'] = 1
        elif rank_pct <= 0.20: item['tier'] = 2
        elif rank_pct <= 0.50: item['tier'] = 3
        elif rank_pct <= 0.80: item['tier'] = 4
        else: item['tier'] = 5
        item['rank'] = idx + 1

    # Peers
    sector_stocks = {}
    for item in results:
        sec = item['sector']
        if sec not in sector_stocks: sector_stocks[sec] = []
        sector_stocks[sec].append(item)
    
    for item in results:
        sec = item['sector']
        peers = [p for p in sector_stocks.get(sec, []) if p['ticker'] != item['ticker']][:3]
        item['related_peers'] = [
            {"ticker": p['ticker'], "change_pct": p['change_pct']} for p in peers
        ]

    with open(OUTPUT_FILE, "w", encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Generated {len(results)} mock items.")

if __name__ == "__main__":
    generate_mock_data()
