import FinanceDataReader as fdr
import pandas as pd
import numpy as np
import time
import json
import random
from tickers import get_all_tickers
from stock_names import get_name
from datetime import datetime, timedelta

# --- Configuration ---
OUTPUT_FILE = "data.json"

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

# Fallback sector mapping for stocks (simplified - can be expanded)
TICKER_SECTORS = {
    "AAPL": "Technology",
    "MSFT": "Technology",
    "NVDA": "Technology",
    "GOOGL": "Communication Services",
    "GOOG": "Communication Services",
    "AMZN": "Consumer Cyclical",
    "META": "Communication Services",
    "TSLA": "Consumer Cyclical",
    # Add more as needed
}

# --- Logic Helpers ---

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
    """Generates AI Briefing based on stats and pivot levels. Ported from mock_data.py"""
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

# --- Scoring Logic ---

def calculate_naspick_score(ticker, history):
    """
    Calculates the Naspick Score based on the provided logic.
    Returns a dictionary with score details and tier.
    
    Note: FinanceDataReader returns DataFrame with columns: Open, High, Low, Close, Volume
    """
    if history.empty or len(history) < 200:
        return None 

    current_price = history['Close'].iloc[-1]
    prev_close = history['Close'].iloc[-2]
    
    # For Pivot Points: Use previous day's OHLC
    yest_high = history['High'].iloc[-2]
    yest_low = history['Low'].iloc[-2]
    yest_close = history['Close'].iloc[-2]
    levels = calculate_pivot_points(yest_high, yest_low, yest_close)

    # Simple Moving Averages
    sma20 = history['Close'].rolling(window=20).mean().iloc[-1]
    sma60 = history['Close'].rolling(window=60).mean().iloc[-1]
    sma100 = history['Close'].rolling(window=100).mean().iloc[-1]
    sma300 = history['Close'].rolling(window=300).mean().iloc[-1]
    
    # RSI (14)
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
    
    # --- PART A: Base Score (80 max) ---
    base_score = 0
    signals = []
    
    # 1. Daily Trend (30)
    trend_score_part = 0
    if current_price > sma20: trend_score_part += 10
    if current_price > sma60: trend_score_part += 10
    if sma20 > sma60: trend_score_part += 10
    base_score += trend_score_part
    
    # 2. Long Term Trend (30)
    if current_price > sma100: trend_score_part += 10
    if current_price > sma300: trend_score_part += 10
    if sma100 > sma300: trend_score_part += 10
    base_score += trend_score_part 
    
    # 3. Indicators (20)
    momentum_score_part = 0
    
    # RSI
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
    
    # MACD
    macd_points = 0
    if macd_val > signal_val:
        macd_points = 10
        signals.append("MACD_GoldenCross")
    
    base_score += macd_points
    momentum_score_part += macd_points

    # --- PART B: Bonus Score (20 max) ---
    bonus_score = 0
    
    # 1. Volume Power (Max 10)
    rvol_score = 0
    if vol_20_avg > 0:
        rvol = curr_vol / vol_20_avg
        rvol_score = (rvol - 1.0) * 5.0
        rvol_score = max(0.0, min(10.0, rvol_score))
    bonus_score += rvol_score
    
    # 2. ATR Score (Max 10)
    atr_score = 0
    if atr > 0:
        price_change = current_price - prev_close
        if price_change > 0:
            atr_ratio = price_change / atr
            atr_score = atr_ratio * 5.0
            atr_score = max(0.0, min(10.0, atr_score))
    bonus_score += atr_score
    
    # Final Score
    final_score = base_score + bonus_score
    final_score = min(100.0, final_score)
    
    # Stats Bar calc
    stats_trend = int((trend_score_part / 60) * 100) if trend_score_part > 0 else 0
    stats_volume = int((rvol_score / 10) * 100)
    stats_momentum = int((momentum_score_part / 20) * 100)
    stats_impact = int((atr_score / 10) * 100)
    
    stats_bar = {
        "trend": min(100, stats_trend),
        "volume": min(100, stats_volume),
        "momentum": min(100, stats_momentum),
        "impact": min(100, stats_impact)
    }

    ai_briefing = generate_ai_briefing(stats_bar, levels, current_price)
    
    change_pct = ((current_price - prev_close) / prev_close) * 100
    
    # Get sector (fallback to ticker lookup or Other)
    sector_en = TICKER_SECTORS.get(ticker, "Technology")  # Default to Technology
    sector_kr = SECTOR_MAP.get(sector_en, sector_en)
    
    # Get name from stock_names.py
    names = get_name(ticker)
    
    return {
        "ticker": ticker,
        "name": names['name'],  # Korean name from stock_names.py
        "name_en": names['name_en'],  # English name from stock_names.py
        "sector": sector_kr,
        "current_price": round(current_price, 2),
        "change_pct": round(change_pct, 2),
        "market_cap": 0,  # FinanceDataReader doesn't provide market cap in price data
        "base_score": base_score,
        "bonus_score": round(bonus_score, 2),
        "final_score": round(final_score, 1),
        "stats_bar": stats_bar,
        "signals": signals,
        "levels": levels,
        "ai_briefing": ai_briefing
    }

def main():
    print("Starting Naspick Scorer [FINANCEDATAREADER MODE]...")
    tickers = get_all_tickers()  # Use all tickers
    print(f"Target Tickers: {len(tickers)} stocks (NASDAQ-100 + S&P 500)")
    
    results = []
    
    # Date range: Last 2 years to ensure we have enough data for 300-day MA
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)  # ~2 years
    
    total = len(tickers)
    for idx, t in enumerate(tickers, 1):
        try:
            print(f"[{idx}/{total}] Fetching data for {t}...")
            hist = fdr.DataReader(t, start_date, end_date)
            
            # print(f"  Data fetched. Shape: {hist.shape}")
            
            res = calculate_naspick_score(t, hist)
            if res:
                results.append(res)
                print(f"  ✓ Processed {t}: Score={res['final_score']}")
            else:
                print(f"  ⚠ Skipped {t}: Insufficient data")
            
        except Exception as e:
            print(f"  ✗ Error processing {t}: {e}")
        
        # Small delay to be nice to the API
        if idx % 10 == 0:
            time.sleep(0.5)
        
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

    # Inject Related Stocks (Same Sector Top 3)
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
    
    print(f"\nDone. Saved {len(results)} items to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
