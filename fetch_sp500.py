#!/usr/bin/env python3
"""
S&P 500 Stock Data Fetcher using FinanceDataReader
More stable and reliable than yfinance
"""

import FinanceDataReader as fdr
import pandas as pd
import json
import time
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# S&P 500 Tickers (top 100 for now)
SP500_TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK.B", "UNH", "XOM",
    "JNJ", "JPM", "V", "PG", "MA", "HD", "CVX", "MRK", "ABBV", "PEP",
    "COST", "AVGO", "KO", "ADBE", "WMT", "MCD", "CRM", "CSCO", "ACN", "LIN",
    "TMO", "NFLX", "ABT", "NKE", "PFE", "DHR", "ORCL", "VZ", "DIS", "CMCSA",
    "TXN", "AMD", "INTC", "PM", "WFC", "NEE", "QCOM", "UPS", "RTX", "INTU",
    "HON", "IBM", "AMGN", "LOW", "SBUX", "SPGI", "GS", "ELV", "BA", "AMAT",
    "BKNG", "AXP", "CAT", "ISRG", "DE", "NOW", "PLD", "ADI", "GILD", "LMT",
    "SYK", "TJX", "VRTX", "ADP", "MDLZ", "MMC", "BX", "REGN", "CVS", "ZTS",
    "CI", "MO", "SCHW", "PGR", "CB", "ETN", "C", "LRCX", "SLB", "SO",
    "BSX", "DUK", "EOG", "GE", "EQIX", "KLAC", "ITW", "APH", "MU", "HUM"
]

# Stock names mapping (Korean names)
STOCK_NAMES = {
    "AAPL": "애플", "MSFT": "마이크로소프트", "GOOGL": "알파벳 A", "AMZN": "아마존",
    "NVDA": "엔비디아", "META": "메타", "TSLA": "테슬라", "BRK.B": "버크셔 해서웨이",
    "UNH": "유나이티드헬스", "XOM": "엑손모빌", "JNJ": "존슨앤존슨", "JPM": "제이피모건",
    "V": "비자", "PG": "P&G", "MA": "마스터카드", "HD": "홈디포", "CVX": "셰브론",
    "MRK": "머크", "ABBV": "애브비", "PEP": "펩시코", "COST": "코스트코",
    "AVGO": "브로드컴", "KO": "코카콜라", "ADBE": "어도비", "WMT": "월마트",
    "MCD": "맥도날드", "CRM": "세일즈포스", "CSCO": "시스코", "ACN": "액센츄어",
    "LIN": "린데", "TMO": "써모피셔", "NFLX": "넷플릭스", "ABT": "애벗",
    "NKE": "나이키", "PFE": "화이자", "DHR": "다나허", "ORCL": "오라클",
    "VZ": "버라이즌", "DIS": "디즈니", "CMCSA": "컴캐스트", "TXN": "텍사스인스트루먼트",
    "AMD": "AMD", "INTC": "인텔", "PM": "필립모리스", "WFC": "웰스파고",
    "NEE": "넥스트에라", "QCOM": "퀄컴", "UPS": "UPS", "RTX": "레이시온",
    "INTU": "인튜잇", "HON": "허니웰", "IBM": "IBM", "AMGN": "암젠",
    "LOW": "로우스", "SBUX": "스타벅스", "SPGI": "S&P글로벌", "GS": "골드만삭스",
}

SECTOR_MAP = {
    "Technology": "기술", "Communication Services": "커뮤니케이션",
    "Consumer Cyclical": "임의소비재", "Consumer Defensive": "필수소비재",
    "Energy": "에너지", "Financial Services": "금융", "Financial": "금융",
    "Healthcare": "헬스케어", "Industrials": "산업재",
    "Basic Materials": "소재", "Real Estate": "부동산", "Utilities": "유틸리티"
}

# Default sector assignments
TICKER_SECTORS = {
    "AAPL": "Technology", "MSFT": "Technology", "GOOGL": "Communication Services",
    "AMZN": "Consumer Cyclical", "NVDA": "Technology", "META": "Communication Services",
    "TSLA": "Consumer Cyclical", "JPM": "Financial", "V": "Financial",
    "MA": "Financial", "WMT": "Consumer Defensive", "JNJ": "Healthcare",
    "UNH": "Healthcare", "PFE": "Healthcare", "MRK": "Healthcare", "ABBV": "Healthcare",
    "XOM": "Energy", "CVX": "Energy", "KO": "Consumer Defensive", "PEP": "Consumer Defensive",
    "PG": "Consumer Defensive", "COST": "Consumer Defensive", "HD": "Consumer Cyclical",
    "NKE": "Consumer Cyclical", "MCD": "Consumer Cyclical", "SBUX": "Consumer Cyclical",
    "DIS": "Communication Services", "NFLX": "Communication Services", "CMCSA": "Communication Services",
    "VZ": "Communication Services", "AMD": "Technology", "INTC": "Technology",
    "NVDA": "Technology", "AVGO": "Technology", "CSCO": "Technology", "ORCL": "Technology",
    "ADBE": "Technology", "CRM": "Technology", "QCOM": "Technology", "TXN": "Technology",
}

def calculate_pivot_points(high, low, close):
    """Calculate pivot points"""
    pivot = (high + low + close) / 3
    r1 = (2 * pivot) - low
    r2 = pivot + (high - low)
    s1 = (2 * pivot) - high
    s2 = pivot - (high - low)
    
    return {
        "pivot": round(pivot, 2), "r1": round(r1, 2), "r2": round(r2, 2),
        "s1": round(s1, 2), "s2": round(s2, 2)
    }

def calculate_rsi(data, period=14):
    """Calculate RSI"""
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1] if len(rsi) > 0 else 50

def generate_ai_briefing(stats, levels, current_price):
    """Generate AI briefing"""
    briefing = []
    
    if stats['trend'] >= 80:
        briefing.append({"id": 1, "title": "강력한 정배열",
            "text": "모든 이동평균선(20, 60, 100) 위에 주가가 위치하며 이상적인 상승 추세를 그리고 있음.",
            "color_class": "text-blue-400"})
    elif stats['trend'] >= 50:
        briefing.append({"id": 1, "title": "추세 전환 시도",
            "text": "단기 하락세를 멈추고 20일 이평선을 돌파하며 의미 있는 반등 시그널 발생.",
            "color_class": "text-[#00bba3]"})
    else:
        briefing.append({"id": 1, "title": "조정 국면",
            "text": "주요 지지선을 이탈하여 약세가 지속 중. 보수적인 접근이 필요함.",
            "color_class": "text-gray-400"})
    
    if stats['volume'] >= 80:
        briefing.append({"id": 2, "title": "수급 집중",
            "text": "평소 대비 2배 이상의 거래량이 터지며 메이저 주체(기관/외인)의 개입이 강력하게 의심됨.",
            "color_class": "text-[#00bba3]"})
    elif stats['volume'] <= 40:
        briefing.append({"id": 2, "title": "거래량 소강",
            "text": "상승 탄력이 둔화되며 거래량이 감소 중. 방향성 탐색 구간.",
            "color_class": "text-gray-400"})
    else:
        briefing.append({"id": 2, "title": "견조한 수급",
            "text": "특이 사항 없이 꾸준한 거래량을 동반하며 추세를 뒷받침하고 있음.",
            "color_class": "text-blue-400"})
    
    simulated_rsi = stats['momentum']
    if simulated_rsi >= 75:
        briefing.append({"id": 3, "title": "과열 주의",
            "text": f"단기 과열 구간 진입. 신규 진입자는 눌림목(${levels['s1']})을 기다리는 것이 유리함.",
            "color_class": "text-rose-400"})
    elif simulated_rsi <= 25:
        briefing.append({"id": 3, "title": "기술적 반등 기대",
            "text": "침체권 진입. 단기 낙폭 과대로 인한 기술적 반등이 기대되는 구간.",
            "color_class": "text-blue-400"})
    else:
        briefing.append({"id": 3, "title": "홀딩 전략",
            "text": f"현재 추세가 유효하므로 1차 지지선(${levels['s1']}) 이탈 전까지는 추세 추종 전략 권장.",
            "color_class": "text-gray-400"})
    
    return briefing

def calculate_naspick_score(ticker, hist):
    """Calculate Naspick score"""
    try:
        if hist.empty or len(hist) < 100:
            return None
        
        current_price = hist['Close'].iloc[-1]
        prev_close = hist['Close'].iloc[-2]
        
        # Pivot points
        yest_high = hist['High'].iloc[-2]
        yest_low = hist['Low'].iloc[-2]
        yest_close = hist['Close'].iloc[-2]
        levels = calculate_pivot_points(yest_high, yest_low, yest_close)
        
        # Moving averages
        sma20 = hist['Close'].rolling(window=20).mean().iloc[-1]
        sma60 = hist['Close'].rolling(window=60).mean().iloc[-1]
        sma100 = hist['Close'].rolling(window=100).mean().iloc[-1]
        
        # RSI
        rsi = calculate_rsi(hist)
        
        # MACD
        exp12 = hist['Close'].ewm(span=12, adjust=False).mean()
        exp26 = hist['Close'].ewm(span=26, adjust=False).mean()
        macd = exp12 - exp26
        signal = macd.ewm(span=9, adjust=False).mean()
        macd_val = macd.iloc[-1]
        signal_val = signal.iloc[-1]
        
        # Volume
        vol_20_avg = hist['Volume'].rolling(window=20).mean().iloc[-1]
        curr_vol = hist['Volume'].iloc[-1]
        
        # Base score
        base_score = 0
        signals = []
        
        # Trend (60 points)
        trend_score = 0
        if current_price > sma20: trend_score += 10
        if current_price > sma60: trend_score += 10
        if sma20 > sma60: trend_score += 10
        if current_price > sma100: trend_score += 10
        if sma60 > sma100: trend_score += 10
        if sma20 > sma100: trend_score += 10
        base_score += trend_score
        
        # Momentum (20 points)
        momentum_score = 0
        if 50 <= rsi <= 75:
            momentum_score += 10
        elif 75 < rsi <= 85:
            momentum_score += 5
            signals.append("RSI_Overbought")
        elif rsi > 85:
            signals.append("RSI_Extreme")
        elif rsi < 30:
            signals.append("RSI_Oversold")
        
        if macd_val > signal_val:
            momentum_score += 10
            signals.append("MACD_GoldenCross")
        
        base_score += momentum_score
        
        # Bonus score (20 points)
        bonus_score = 0
        
        # Volume
        if vol_20_avg > 0:
            rvol = curr_vol / vol_20_avg
            rvol_score = (rvol - 1.0) * 5.0
            rvol_score = max(0.0, min(10.0, rvol_score))
            bonus_score += rvol_score
        
        # Price momentum
        price_change = current_price - prev_close
        if price_change > 0:
            momentum_boost = min(10.0, abs(price_change / prev_close) * 100 * 2)
            bonus_score += momentum_boost
        
        final_score = min(100.0, base_score + bonus_score)
        
        # Stats bars
        stats_trend = int((trend_score / 60) * 100)
        stats_volume = int((rvol_score / 10) * 100) if 'rvol_score' in locals() else 50
        stats_momentum = int((momentum_score / 20) * 100)
        stats_impact = int((bonus_score / 20) * 100)
        
        stats_bar = {
            "trend": min(100, stats_trend),
            "volume": min(100, stats_volume),
            "momentum": min(100, stats_momentum),
            "impact": min(100, stats_impact)
        }
        
        ai_briefing = generate_ai_briefing(stats_bar, levels, current_price)
        change_pct = ((current_price - prev_close) / prev_close) * 100
        
        # Get sector
        sector_en = TICKER_SECTORS.get(ticker, "Technology")
        sector_kr = SECTOR_MAP.get(sector_en, sector_en)
        
        name = STOCK_NAMES.get(ticker, ticker)
        
        return {
            "ticker": ticker,
            "name": name,
            "name_en": ticker,
            "sector": sector_kr,
            "current_price": round(current_price, 2),
            "change_pct": round(change_pct, 2),
            "market_cap": 0,
            "base_score": base_score,
            "bonus_score": round(bonus_score, 2),
            "final_score": round(final_score, 1),
            "stats_bar": stats_bar,
            "signals": signals,
            "levels": levels,
            "ai_briefing": ai_briefing
        }
    except Exception as e:
        print(f"  ✗ Error for {ticker}: {e}")
        return None

def main():
    print("🚀 Fetching S&P 500 Stock Data with FinanceDataReader")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Total tickers: {len(SP500_TICKERS)}\n")
    
    results = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    for idx, ticker in enumerate(SP500_TICKERS, 1):
        try:
            print(f"[{idx}/{len(SP500_TICKERS)}] Fetching {ticker}...", end=" ")
            
            # Fetch data using FinanceDataReader
            hist = fdr.DataReader(ticker, start_date, end_date)
            
            if hist.empty or len(hist) < 100:
                print(f"⚠ Insufficient data ({len(hist)} days)")
                continue
            
            # Calculate score
            result = calculate_naspick_score(ticker, hist)
            if result:
                results.append(result)
                print(f"✓ ${result['current_price']} → Score {result['final_score']}")
            else:
                print(f"✗ Failed")
            
            # Small delay
            if idx % 10 == 0:
                time.sleep(1)
            
        except Exception as e:
            print(f"✗ Error: {str(e)[:50]}")
            continue
    
    if not results:
        print("\n❌ No data fetched!")
        return
    
    # Sort and tier
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
    
    # Related peers
    sector_stocks = {}
    for item in results:
        sec = item['sector']
        if sec not in sector_stocks:
            sector_stocks[sec] = []
        sector_stocks[sec].append(item)
    
    for item in results:
        sec = item['sector']
        peers = [p for p in sector_stocks.get(sec, []) if p['ticker'] != item['ticker']][:3]
        item['related_peers'] = [
            {"ticker": p['ticker'], "change_pct": p['change_pct']} for p in peers
        ]
    
    # Save
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Success! Saved {len(results)} stocks to data.json")
    print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
