import yfinance as yf
import pandas as pd
import numpy as np
import json
from tickers import get_all_tickers
from stock_names import get_name
from datetime import datetime, timedelta

# --- Configuration ---
OUTPUT_FILE = "data.json"
BATCH_SIZE = 50  # Process 50 tickers at a time

# --- Mapping & Constants ---
SECTOR_MAP = {
    "Technology": "기술",
    "Communication Services": "커뮤니케이션",
    "Consumer Cyclical": "임의소비재",
    "Consumer Defensive": "필수소비재",
    "Energy": "에너지",
    "Financial Services": "금융",
    "Healthcare": "헬스케어",
    "Industrials": "산업재",
    "Basic Materials": "소재",
    "Real Estate": "부동산",
    "Utilities": "유틸리티"
}

# --- Helper Functions (same as scorer.py) ---

def calculate_pivot_points(high, low, close):
    """Calculates Standard Pivot Points."""
    pivot = (high + low + close) / 3
    r1 = (2 * pivot) - low
    r2 = pivot + (high - low)
    s1 = (2 * pivot) - high
    s2 = pivot - (high - low)
    
    return {
        "pivot": round(pivot, 2),
        "r1": round(r1, 2),
        "r2": round(r2, 2),
        "s1": round(s1, 2),
        "s2": round(s2, 2)
    }

def generate_ai_briefing(stats, levels, current_price):
    """Generates AI Briefing based on stats and pivot levels."""
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
    simulated_rsi = stats['momentum'] 
    
    if simulated_rsi >= 75:
        briefing.append({
            "id": 3,
            "title": "과열 주의",
            "text": f"단기 과열 구간 진입. 신규 진입자는 눌림목(${levels['s1']})을 기다리는 것이 유리함.",
            "color_class": "text-rose-400"
        })
    elif simulated_rsi <= 25:
         briefing.append({
            "id": 3,
            "title": "기술적 반등 기대",
            "text": "침체권 진입. 단기 낙폭 과대로 인한 기술적 반등이 기대되는 구간.",
            "color_class": "text-blue-400"
        })
    else:
         briefing.append({
            "id": 3,
            "title": "홀딩 전략",
            "text": f"현재 추세가 유효하므로 1차 지지선(${levels['s1']}) 이탈 전까지는 추세 추종 전략 권장.",
            "color_class": "text-gray-400"
        })
        
    return briefing

def calculate_naspick_score(ticker, info, history):
    """Calculate Naspick Score for a single ticker."""
    if history.empty or len(history) < 200:
        return None 

    current_price = history['Close'].iloc[-1]
    prev_close = history['Close'].iloc[-2]
    
    # Pivot Points
    yest_high = history['High'].iloc[-2]
    yest_low = history['Low'].iloc[-2]
    yest_close = history['Close'].iloc[-2]
    levels = calculate_pivot_points(yest_high, yest_low, yest_close)

    # Moving Averages
    sma20 = history['Close'].rolling(window=20).mean().iloc[-1]
    sma60 = history['Close'].rolling(window=60).mean().iloc[-1]
    sma100 = history['Close'].rolling(window=100).mean().iloc[-1]
    sma300 = history['Close'].rolling(window=300).mean().iloc[-1]
    
    # RSI
    delta = history['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs)).iloc[-1]
    
    # MACD
    exp12 = history['Close'].ewm(span=12, adjust=False).mean()
    exp26 = history['Close'].ewm(span=26, adjust=False).mean()
    macd = exp12 - exp26
    signal = macd.ewm(span=9, adjust=False).mean()
    macd_val = macd.iloc[-1]
    signal_val = signal.iloc[-1]
    
    # Volume & ATR
    vol_20_avg = history['Volume'].rolling(window=20).mean().iloc[-1]
    curr_vol = history['Volume'].iloc[-1]
    
    tr = pd.DataFrame()
    tr['h-l'] = history['High'] - history['Low']
    tr['h-pc'] = abs(history['High'] - history['Close'].shift(1))
    tr['l-pc'] = abs(history['Low'] - history['Close'].shift(1))
    tr['tr'] = tr[['h-l', 'h-pc', 'l-pc']].max(axis=1)
    atr = tr['tr'].rolling(window=20).mean().iloc[-1]
    
    # Base Score Calculation
    base_score = 0
    signals = []
    trend_score_part = 0
    
    # Daily & Long Term Trend
    if current_price > sma20: trend_score_part += 10
    if current_price > sma60: trend_score_part += 10
    if sma20 > sma60: trend_score_part += 10
    if current_price > sma100: trend_score_part += 10
    if current_price > sma300: trend_score_part += 10
    if sma100 > sma300: trend_score_part += 10
    base_score += trend_score_part
    
    # Indicators
    momentum_score_part = 0
    rsi_points = 0
    if 50 <= rsi <= 75:
        rsi_points = 10
    elif 75 < rsi <= 85:
        rsi_points = 5
        signals.append("RSI_Overbought")
    elif rsi > 85:
        signals.append("RSI_Extreme")
    elif rsi < 30:
        signals.append("RSI_Oversold")
    
    base_score += rsi_points
    momentum_score_part += rsi_points
    
    macd_points = 0
    if macd_val > signal_val:
        macd_points = 10
        signals.append("MACD_GoldenCross")
    
    base_score += macd_points
    momentum_score_part += macd_points

    # Bonus Score
    bonus_score = 0
    rvol_score = 0
    if vol_20_avg > 0:
        rvol = curr_vol / vol_20_avg
        rvol_score = (rvol - 1.0) * 5.0
        rvol_score = max(0.0, min(10.0, rvol_score))
    bonus_score += rvol_score
    
    atr_score = 0
    if atr > 0:
        price_change = current_price - prev_close
        if price_change > 0:
            atr_ratio = price_change / atr
            atr_score = atr_ratio * 5.0
            atr_score = max(0.0, min(10.0, atr_score))
    bonus_score += atr_score
    
    final_score = min(100.0, base_score + bonus_score)
    
    # Stats Bar
    stats_bar = {
        "trend": min(100, int((trend_score_part / 60) * 100)),
        "volume": min(100, int((rvol_score / 10) * 100)),
        "momentum": min(100, int((momentum_score_part / 20) * 100)),
        "impact": min(100, int((atr_score / 10) * 100))
    }

    ai_briefing = generate_ai_briefing(stats_bar, levels, current_price)
    change_pct = ((current_price - prev_close) / prev_close) * 100
    
    # Get names
    names = get_name(ticker)
    
    return {
        "ticker": ticker,
        "name": names['name'],
        "name_en": names['name_en'],
        "sector": SECTOR_MAP.get(info.get('sector', ''), info.get('sector', '기타')),
        "current_price": round(current_price, 2),
        "change_pct": round(change_pct, 2),
        "market_cap": info.get('marketCap', 0),
        "base_score": base_score,
        "bonus_score": round(bonus_score, 2),
        "final_score": round(final_score, 1),
        "stats_bar": stats_bar,
        "signals": signals,
        "levels": levels,
        "ai_briefing": ai_briefing
    }

def main():
    print("Starting Naspick Scorer [YFINANCE BATCH MODE]...")
    print("이 버전은 배치 요청으로 API 호출을 최소화합니다.\n")
    
    tickers = get_all_tickers()
    print(f"Total Tickers: {len(tickers)}")
    
    results = []
    
    # Process in batches
    for i in range(0, len(tickers), BATCH_SIZE):
        batch = tickers[i : i + BATCH_SIZE]
        print(f"\nBatch {i//BATCH_SIZE + 1}/{(len(tickers)-1)//BATCH_SIZE + 1}: {len(batch)} tickers")
        
        try:
            # Batch download - MUCH faster!
            tickers_str = " ".join(batch)
            print(f"  Downloading batch...")
            data = yf.download(tickers_str, period="2y", group_by='ticker', auto_adjust=True, threads=True, progress=False)
            
            # Process each ticker
            for t in batch:
                try:
                    # Extract data for this ticker
                    if len(batch) == 1:
                        hist = data
                    else:
                        hist = data[t] if t in data.columns.get_level_values(0) else pd.DataFrame()
                    
                    if hist.empty or len(hist) < 200:
                        print(f"  {t}: Insufficient data")
                        continue
                    
                    # Get info (separate call, but necessary for sector/market cap)
                    stock = yf.Ticker(t)
                    info = stock.info
                    
                    res = calculate_naspick_score(t, info, hist)
                    if res:
                        results.append(res)
                        print(f"  {t}: Score={res['final_score']}")
                    
                except Exception as e:
                    print(f"  {t}: Error - {e}")
            
        except Exception as e:
            print(f"  Batch download failed: {e}")
            # Fallback to individual downloads
            for t in batch:
                try:
                    stock = yf.Ticker(t)
                    hist = stock.history(period="2y")
                    info = stock.info
                    
                    res = calculate_naspick_score(t, info, hist)
                    if res:
                        results.append(res)
                        print(f"  {t}: Score={res['final_score']}")
                except Exception as e2:
                    print(f"  {t}: Error - {e2}")

    # Sort and Tier
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

    # Related Peers
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

    # Save
    with open(OUTPUT_FILE, "w", encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Done! Saved {len(results)} items to {OUTPUT_FILE}")
    print(f"\n통계:")
    print(f"  - 성공: {len(results)}/{len(tickers)} ({len(results)/len(tickers)*100:.1f}%)")
    print(f"  - Tier 1: {sum(1 for r in results if r['tier'] == 1)}")
    print(f"  - Tier 2: {sum(1 for r in results if r['tier'] == 2)}")
    print(f"  - Tier 3: {sum(1 for r in results if r['tier'] == 3)}")

if __name__ == "__main__":
    main()
