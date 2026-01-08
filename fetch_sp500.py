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

# Get S&P 500 list dynamically
def get_sp500_tickers():
    """Fetch latest S&P 500 list from FinanceDataReader"""
    try:
        sp500 = fdr.StockListing('SP500')
        return sp500['Symbol'].tolist()
    except:
        # Fallback to basic list if API fails
        return [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK.B", "UNH", "XOM",
            "JNJ", "JPM", "V", "PG", "MA", "HD", "CVX", "MRK", "ABBV", "PEP"
        ]

SP500_TICKERS = get_sp500_tickers()

# Ensure dual class shares and handle dot notation
REQUIRED_TICKERS = ['BRK.B', 'BF.B', 'GOOGL', 'GOOG', 'FOXA', 'FOX', 'NWSA', 'NWS']
for t in REQUIRED_TICKERS:
    # Remove hyphenated versions if present to standardise on dot
    t_hyphen = t.replace('.', '-')
    if t_hyphen in SP500_TICKERS:
        SP500_TICKERS.remove(t_hyphen)
    if t not in SP500_TICKERS:
        SP500_TICKERS.append(t)

# Remove duplicates
SP500_TICKERS = list(set(SP500_TICKERS))

# Map for fetching (Yahoo uses hyphen)
FETCH_MAP = {
    'BRK.B': 'BRK-B',
    'BF.B': 'BF-B'
}

print(f"✓ Loaded {len(SP500_TICKERS)} S&P 500 tickers (Adjusted for dual classes)")

# Import Korean names
from sp500_korean_names import SP500_KOREAN_NAMES
STOCK_NAMES = SP500_KOREAN_NAMES

SECTOR_MAP = {
    "Technology": "기술", 
    "Information Technology": "기술",
    "Communication Services": "커뮤니케이션",
    "Consumer Cyclical": "임의소비재", 
    "Consumer Discretionary": "임의소비재",
    "Consumer Defensive": "필수소비재",
    "Consumer Staples": "필수소비재",
    "Energy": "에너지", 
    "Financial Services": "금융", 
    "Financials": "금융",
    "Financial": "금융",
    "Healthcare": "헬스케어", 
    "Health Care": "헬스케어",
    "Industrials": "산업재",
    "Basic Materials": "소재", 
    "Materials": "소재",
    "Real Estate": "부동산", 
    "Utilities": "유틸리티"
}

# Fetch accurate sector data
def get_sector_data():
    try:
        sp500 = fdr.StockListing('SP500')
        sectors = dict(zip(sp500['Symbol'], sp500['Sector']))
        # Manual overrides
        sectors['BRK.B'] = 'Financials'
        sectors['BF.B'] = 'Consumer Staples'
        return sectors
    except:
        return {}

REAL_SECTORS = get_sector_data()

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
    "ADBE": "Technology", "CRM": "Technology", "QCOM": "Technology", "TXN": "Technology",
}

# Fetch exchange data
def get_exchange_data():
    print("  - Fetching exchange listings (NASDAQ, NYSE, AMEX)...")
    try:
        exchanges = {}
        # NASDAQ
        nasdaq = fdr.StockListing('NASDAQ')
        for t in nasdaq['Symbol']: exchanges[t] = 'NASDAQ'
        # NYSE
        nyse = fdr.StockListing('NYSE')
        for t in nyse['Symbol']: exchanges[t] = 'NYSE'
        # AMEX
        amex = fdr.StockListing('AMEX')
        for t in amex['Symbol']: exchanges[t] = 'AMEX'
        
        # Manual overrides
        exchanges['BRK.B'] = 'NYSE'
        exchanges['BF.B'] = 'NYSE'
        exchanges['DAY'] = 'NYSE' # Ensure DAY is correct
        
        return exchanges
    except Exception as e:
        print(f"  ⚠ Exchange fetch failed: {e}")
        return {}

REAL_EXCHANGES = get_exchange_data()

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

def generate_ai_briefing(stats, levels, current_price, context):
    """Generate AI briefing with advanced logic"""
    briefing = []
    
    # 1. Trend Analysis (MACD & Moving Averages)
    if context.get('macd_golden'):
        briefing.append({"id": 1, "title": "MACD 골든크로스",
            "text": "MACD 골든크로스가 발생하여 단기적인 상승 추세로의 전환 신호가 포착되었습니다.",
            "color_class": "text-blue-400"})
    elif context.get('macd_dead'):
        briefing.append({"id": 1, "title": "MACD 데드크로스",
            "text": "MACD 데드크로스 발생, 단기 조정 압력이 거세질 수 있어 리스크 관리가 필요합니다.",
            "color_class": "text-rose-400"})
    elif context.get('candle_hammer'):
         briefing.append({"id": 1, "title": "바닥권 매수세",
            "text": "하락세 끝에서 저점 매수세가 유입되는 '망치형' 캔들이 발생했습니다. 바닥 다지기를 시도 중입니다.",
            "color_class": "text-blue-400"})
    elif stats['trend'] >= 80:
        if stats['momentum'] >= 75: # Context: Strong but Overbought
             briefing.append({"id": 1, "title": "강력한 상승세",
            "text": "파죽지세의 상승세를 보이고 있으나, RSI 과열권에 진입하여 건전한 '숨고르기' 조정을 염두에 둬야 합니다.",
            "color_class": "text-blue-400"})
        else:
            briefing.append({"id": 1, "title": "이상적 정배열",
                "text": "주가가 모든 이동평균선(20, 60, 100) 상단에 위치하며, 가장 이상적이고 강력한 상승 추세를 유지하고 있습니다.",
                "color_class": "text-blue-400"})
    elif stats['trend'] >= 50:
        briefing.append({"id": 1, "title": "추세 전환 시도",
            "text": "단기 하락세를 멈추고 20일 이평선을 돌파하며 의미 있는 반등 시그널이 발생했습니다.",
            "color_class": "text-[#00bba3]"})
    else:
        briefing.append({"id": 1, "title": "조정 국면",
            "text": "주요 지지선을 이탈하여 약세가 지속 중입니다. 섣부른 진입보다는 지지선 확인이 필요한 보수적 구간입니다.",
            "color_class": "text-gray-400"})
    
    # 2. Volume & Volatility (Bollinger & Volume)
    if context.get('bb_breakout'):
        briefing.append({"id": 2, "title": "볼린저 밴드 돌파",
            "text": "볼린저 밴드 상단을 강하게 돌파하며 시세가 분출되고 있습니다. 강력한 모멘텀이 발생했습니다.",
            "color_class": "text-blue-400"})
    elif context.get('bb_squeeze'):
        briefing.append({"id": 2, "title": "변동성 축소 (Squeeze)",
            "text": "변동성이 극도로 축소된 '스퀴즈' 구간입니다. 조만간 큰 방향성(급등 또는 급락)이 결정될 것입니다.",
            "color_class": "text-[#00bba3]"})
    elif stats['volume'] >= 80:
        briefing.append({"id": 2, "title": "수급 집중",
            "text": "평소 대비 2배 이상의 대량 거래량이 터지며 메이저 주체(기관/외인)의 강력한 개입이 의심됩니다.",
            "color_class": "text-[#00bba3]"})
    elif stats['volume'] <= 40:
        briefing.append({"id": 2, "title": "거래량 소강",
            "text": "상승 탄력이 둔화되며 거래량이 감소하고 있습니다. 시장의 관심에서 멀어진 방향성 탐색 구간입니다.",
            "color_class": "text-gray-400"})
    else:
        briefing.append({"id": 2, "title": "견조한 수급",
            "text": "특이 사항 없이 꾸준한 거래량을 동반하며 현재의 추세를 안정적으로 뒷받침하고 있습니다.",
            "color_class": "text-blue-400"})
    
    # 3. Strategy (Candle Patterns & Support/Resistance)
    if context.get('candle_shooting'):
        briefing.append({"id": 3, "title": "고점 경계 (유성형)",
            "text": "상승 추세 고점에서 긴 윗꼬리를 단 '유성형' 캔들이 관측됩니다. 차익실현 매물을 주의해야 합니다.",
            "color_class": "text-rose-400"})
    elif context.get('support_defense'):
        briefing.append({"id": 3, "title": "지지선 방어 성공",
            "text": f"주요 지지선인 ${levels['s1']} 가격대를 장중 터치했으나 지켜내며 저가 매수세가 살아있음을 증명했습니다.",
            "color_class": "text-blue-400"})
    elif stats['momentum'] >= 75:
        briefing.append({"id": 3, "title": "과열권 진입",
            "text": f"RSI 과열권에 진입했습니다. 추격 매수보다는 눌림목(${levels['s1']}) 지지를 확인할 때까지 기다리는 것이 유리합니다.",
            "color_class": "text-rose-400"})
    elif stats['momentum'] <= 25:
        briefing.append({"id": 3, "title": "기술적 반등 기대",
            "text": "과매도(침체) 구간에 진입했습니다. 단기 낙폭 과대로 인한 기술적 반등(Dead Cat Bounce)이 기대되는 위치입니다.",
            "color_class": "text-blue-400"})
    else:
        briefing.append({"id": 3, "title": "홀딩 전략",
            "text": f"현재 추세가 유효하므로 1차 지지선(${levels['s1']})을 이탈하지 않는 한 추세 추종(Trend Following) 전략을 권장합니다.",
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
        
        # Bollinger Bands (20, 2)
        sma20_series = hist['Close'].rolling(window=20).mean()
        std20_series = hist['Close'].rolling(window=20).std()
        upper_band = (sma20_series + (std20_series * 2)).iloc[-1]
        lower_band = (sma20_series - (std20_series * 2)).iloc[-1]
        bandwidth = (upper_band - lower_band) / sma20_series.iloc[-1]
        
        # Bandwidth history for squeeze (last 20 days)
        past_bandwidth = ((sma20_series + (std20_series * 2)) - (sma20_series - (std20_series * 2))) / sma20_series
        is_squeeze = bandwidth <= past_bandwidth.rolling(window=20).min().iloc[-1]

        # RSI
        rsi = calculate_rsi(hist)
        
        # MACD
        exp12 = hist['Close'].ewm(span=12, adjust=False).mean()
        exp26 = hist['Close'].ewm(span=26, adjust=False).mean()
        macd = exp12 - exp26
        signal = macd.ewm(span=9, adjust=False).mean()
        macd_val = macd.iloc[-1]
        signal_val = signal.iloc[-1]
        
        # MACD Cross Check (Today or Yesterday)
        macd_prev = macd.iloc[-2]
        signal_prev = signal.iloc[-2]
        
        macd_golden = (macd_prev < signal_prev) and (macd_val > signal_val)
        macd_dead = (macd_prev > signal_prev) and (macd_val < signal_val)
        
        # Volume
        vol_20_avg = hist['Volume'].rolling(window=20).mean().iloc[-1]
        curr_vol = hist['Volume'].iloc[-1]
        
        # Candlestick Patterns
        open_p = hist['Open'].iloc[-1]
        close_p = hist['Close'].iloc[-1]
        high_p = hist['High'].iloc[-1]
        low_p = hist['Low'].iloc[-1]
        body = abs(close_p - open_p)
        upper_shadow = high_p - max(open_p, close_p)
        lower_shadow = min(open_p, close_p) - low_p
        
        # Hammer: Downtrend + Long Lower Shadow
        is_hammer = (current_price < sma20) and (lower_shadow > body * 2) and (upper_shadow < body * 0.5)
        # Shooting Star: Uptrend + Long Upper Shadow
        is_shooting = (current_price > sma20) and (upper_shadow > body * 2) and (lower_shadow < body * 0.5)
        
        # Support Defense: Low touched S1 but Close > S1
        is_support_defense = (low_p <= levels['s1']) and (close_p > levels['s1'])

        # Context for AI Briefing
        context = {
            "macd_golden": macd_golden,
            "macd_dead": macd_dead,
            "bb_breakout": (current_price > upper_band) and (rsi < 75),
            "bb_squeeze": is_squeeze,
            "candle_hammer": is_hammer,
            "candle_shooting": is_shooting,
            "support_defense": is_support_defense
        }

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
        
        ai_briefing = generate_ai_briefing(stats_bar, levels, current_price, context)
        change_pct = ((current_price - prev_close) / prev_close) * 100
        
        # Get sector
        # Try to get from real data first, then fallback to manual map
        raw_sector = REAL_SECTORS.get(ticker)
        if not raw_sector:
             # Try hyphenated for lookup if needed
             raw_sector = REAL_SECTORS.get(ticker.replace('.', '-'))
             
        if not raw_sector:
             raw_sector = TICKER_SECTORS.get(ticker, "Technology")
             
        sector_kr = SECTOR_MAP.get(raw_sector, raw_sector)
        
        name = STOCK_NAMES.get(ticker, ticker)
        
        # Get exchange
        # Try exact match, then hyphenated
        exchange = REAL_EXCHANGES.get(ticker)
        if not exchange:
            exchange = REAL_EXCHANGES.get(ticker.replace('.', '-'), "NASDAQ")
        
        return {
            "ticker": ticker,
            "name": name,
            "name_en": ticker,
            "exchange": exchange,
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
    
    print(f"📊 Total tickers: {len(SP500_TICKERS)}\n")
    
    # Load previous data for rank comparison
    previous_ranks = {}
    try:
        import os
        if os.path.exists('data.json'):
            with open('data.json', 'r', encoding='utf-8') as f:
                old_data = json.load(f)
                for item in old_data:
                    # Map ticker to its previous rank
                    previous_ranks[item['ticker']] = item.get('rank', 9999) # Default to low rank if missing
            print(f"✓ Loaded previous rankings for {len(previous_ranks)} tickers")
    except Exception as e:
        print(f"⚠ Could not load previous data: {e}")

    results = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    for idx, ticker in enumerate(SP500_TICKERS, 1):
        try:
            print(f"[{idx}/{len(SP500_TICKERS)}] Fetching {ticker}...", end=" ")
            
            # Fetch data using FinanceDataReader
            fetch_ticker = FETCH_MAP.get(ticker, ticker)
            hist = fdr.DataReader(fetch_ticker, start_date, end_date)
            
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
        
        # Rank Logic
        current_rank = idx + 1
        item['rank'] = current_rank
        
        # Calculate Rank Change (Old Rank - New Rank)
        # e.g., Old 5, New 1 => Change +4 (Up 4 steps)
        # e.g., Old 1, New 5 => Change -4 (Down 4 steps)
        old_rank = previous_ranks.get(item['ticker'])
        
        if old_rank:
            rank_change = old_rank - current_rank
            item['rank_change'] = rank_change
        else:
            item['rank_change'] = 0 # New entry or first run
    
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
