#!/usr/bin/env python3
"""
S&P 500 Stock Data Fetcher using FinanceDataReader
Updated: v1.1 Sector Relative Scoring
"""

import FinanceDataReader as fdr
import pandas as pd
import numpy as np
import json
import time
import os
import yfinance as yf
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
# Try-catch to handle if file missing (though likely present)
try:
    from sp500_korean_names import SP500_KOREAN_NAMES
    STOCK_NAMES = SP500_KOREAN_NAMES
except ImportError:
    STOCK_NAMES = {}

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
    # print("  - Fetching exchange listings (NASDAQ, NYSE, AMEX)...")
    try:
        exchanges = {}
        # NASDAQ
        try:
            nasdaq = fdr.StockListing('NASDAQ')
            for t in nasdaq['Symbol']: exchanges[t] = 'NASDAQ'
        except: pass
        
        # NYSE
        try:
            nyse = fdr.StockListing('NYSE')
            for t in nyse['Symbol']: exchanges[t] = 'NYSE'
        except: pass

        # AMEX
        try:
            amex = fdr.StockListing('AMEX')
            for t in amex['Symbol']: exchanges[t] = 'AMEX'
        except: pass
        
        # Manual overrides
        exchanges['BRK.B'] = 'NYSE'
        exchanges['BF.B'] = 'NYSE'
        exchanges['DAY'] = 'NYSE' # Ensure DAY is correct
        
        return exchanges
    except Exception as e:
        # print(f"  ⚠ Exchange fetch failed: {e}")
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


# --------------------------------------------------------------------------------
# NEW SCORING ENGINE (v1.1 - Sector Relative + Financials)
# --------------------------------------------------------------------------------

def calculate_technical_factors_bulk(df):
    """Bulk calculation of technical factors for all tickers"""
    print("📈 Calculating Technical Factors (Momentum & Vol)...")
    
    # Ensure sorted
    df = df.sort_values(['Ticker', 'Date'])
    
    # Returns (Momentum)
    # Using 'fill_method=None' to avoid future warnings
    df['Return_12M'] = df.groupby('Ticker')['Close'].pct_change(periods=252, fill_method=None)
    df['Return_6M'] = df.groupby('Ticker')['Close'].pct_change(periods=126, fill_method=None)
    df['Return_3M'] = df.groupby('Ticker')['Close'].pct_change(periods=63, fill_method=None)
    
    # Volume Spike: Current Vol / 3M Avg Vol
    df['Vol_3M_Avg'] = df.groupby('Ticker')['Volume'].transform(lambda x: x.rolling(window=63).mean())
    df['Vol_Spike'] = df['Volume'] / df['Vol_3M_Avg']
    
    return df

def apply_masks_and_score_bulk(daily_df, financial_map):
    """
    Apply Sector Relative Scoring (The Core Logic)
    """
    # Merge financials
    merged = daily_df.merge(financial_map, on='Ticker', how='left')
    
    # Filter unknown sectors
    merged = merged.dropna(subset=['Sector'])
    
    # 1. Mask Negative Valuations (Give them NaN so they rank poorly or handled later)
    # Actually for "Low is Good", if we fillna with high number, it ranks bad.
    # Logic in engine.py: mask negative to NaN.
    val_cols = ['PER', 'PBR', 'EV_EBITDA', 'PSR']
    for col in val_cols:
        if col in merged.columns:
            merged[col] = merged[col].apply(lambda x: x if x > 0 else np.nan)
            
    # 2. Sector Relative Ranking (0.0 to 1.0)
    
    # A. Value (25 pts) - Low is Good
    # Note: NaN values in 'PER' (negatives) will be ranked?
    # Pandas rank handles NaN: assigns NaN. We fillna(0) score later.
    merged['Score_PER'] = (1 - merged.groupby('Sector')['PER'].rank(pct=True, ascending=True)) * 10
    merged['Score_PBR'] = (1 - merged.groupby('Sector')['PBR'].rank(pct=True, ascending=True)) * 5
    merged['Score_PSR'] = (1 - merged.groupby('Sector')['PSR'].rank(pct=True, ascending=True)) * 5
    merged['Score_EVEB'] = (1 - merged.groupby('Sector')['EV_EBITDA'].rank(pct=True, ascending=True)) * 5
    
    # B. Growth (25 pts) - High is Good
    merged['Score_RevG'] = merged.groupby('Sector')['Rev_Growth'].rank(pct=True, ascending=True) * 10
    # Boost EPS weight as per engine logic
    merged['Score_EPSG'] = merged.groupby('Sector')['EPS_Growth'].rank(pct=True, ascending=True) * 15
    
    # C. Profitability (20 pts) - High is Good
    merged['Score_ROE'] = merged.groupby('Sector')['ROE'].rank(pct=True, ascending=True) * 10
    # Map Profit_Margin/Oper_Margin if columns exist
    if 'Profit_Margin' in merged.columns:
        merged['Score_NM'] = merged.groupby('Sector')['Profit_Margin'].rank(pct=True, ascending=True) * 5
    else:
        merged['Score_NM'] = 0
        
    if 'Oper_Margin' in merged.columns:
        merged['Score_OM'] = merged.groupby('Sector')['Oper_Margin'].rank(pct=True, ascending=True) * 5
    else:
        merged['Score_OM'] = 0
        
    # D. Momentum (20 pts) - High is Good
    merged['Score_Mom1Y'] = merged.groupby('Sector')['Return_12M'].rank(pct=True, ascending=True) * 10
    merged['Score_Mom6M'] = merged.groupby('Sector')['Return_6M'].rank(pct=True, ascending=True) * 5
    merged['Score_Mom3M'] = merged.groupby('Sector')['Return_3M'].rank(pct=True, ascending=True) * 5
    
    # E. Sentiment (10 pts) - High is Good (Volume Spike)
    merged['Score_Vol'] = merged.groupby('Sector')['Vol_Spike'].rank(pct=True, ascending=True) * 10
    
    # 3. Fill NaNs with 0 (Penalty for missing/negative data)
    score_cols = [c for c in merged.columns if c.startswith('Score_')]
    merged[score_cols] = merged[score_cols].fillna(0)
    
    # 4. Total Score
    merged['Total_Score'] = merged[score_cols].sum(axis=1)
    
    # Final Rank
    merged['Rank'] = merged['Total_Score'].rank(ascending=False, method='min')
    
    return merged

def analyze_single_stock_context(ticker, hist, final_score_row):
    """
    Generate Technical Context and Briefing for a single stock
    (Used for the UI popup)
    """
    try:
        current_price = hist['Close'].iloc[-1]
        prev_close = hist['Close'].iloc[-2]
        
        # Pivot points
        yest_high = hist['High'].iloc[-2]
        yest_low = hist['Low'].iloc[-2]
        yest_close = hist['Close'].iloc[-2]
        levels = calculate_pivot_points(yest_high, yest_low, yest_close)
        
        # Moving averages
        sma20 = hist['Close'].rolling(window=20).mean().iloc[-1]
        
        # Bollinger Bands
        sma20_series = hist['Close'].rolling(window=20).mean()
        std20_series = hist['Close'].rolling(window=20).std()
        upper_band = (sma20_series + (std20_series * 2)).iloc[-1]
        lower_band = (sma20_series - (std20_series * 2)).iloc[-1]
        
        # Bandwidth squeeze
        bandwidth = (upper_band - lower_band) / sma20_series.iloc[-1]
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
        
        macd_prev = macd.iloc[-2]
        signal_prev = signal.iloc[-2]
        macd_golden = (macd_prev < signal_prev) and (macd_val > signal_val)
        macd_dead = (macd_prev > signal_prev) and (macd_val < signal_val)
        
        # Candle Patterns
        open_p = hist['Open'].iloc[-1]
        close_p = hist['Close'].iloc[-1]
        high_p = hist['High'].iloc[-1]
        low_p = hist['Low'].iloc[-1]
        body = abs(close_p - open_p)
        upper_shadow = high_p - max(open_p, close_p)
        lower_shadow = min(open_p, close_p) - low_p
        
        is_hammer = (current_price < sma20) and (lower_shadow > body * 2) and (upper_shadow < body * 0.5)
        is_shooting = (current_price > sma20) and (upper_shadow > body * 2) and (lower_shadow < body * 0.5)
        is_support_defense = (low_p <= levels['s1']) and (close_p > levels['s1'])

        context = {
            "macd_golden": macd_golden,
            "macd_dead": macd_dead,
            "bb_breakout": (current_price > upper_band) and (rsi < 75),
            "bb_squeeze": is_squeeze,
            "candle_hammer": is_hammer,
            "candle_shooting": is_shooting,
            "support_defense": is_support_defense
        }
        
        # Signals list for UI
        signals = []
        if rsi > 70: signals.append("RSI_Overbought")
        elif rsi < 30: signals.append("RSI_Oversold")
        if macd_golden: signals.append("MACD_GoldenCross")
        if is_squeeze: signals.append("Vol_Squeeze")
        
        # Create Stats Bar from Score (Normalized to 0-100)
        # Value = PER + PBR + PSR + EVEB (Max 25)
        val_score = final_score_row['Score_PER'] + final_score_row['Score_PBR'] + final_score_row['Score_PSR'] + final_score_row['Score_EVEB']
        # Growth = Rev + EPS (Max 25)
        growth_score = final_score_row['Score_RevG'] + final_score_row['Score_EPSG']
        # Profit = ROE + NM + OM (Max 20)
        prof_score = final_score_row['Score_ROE'] + final_score_row['Score_NM'] + final_score_row['Score_OM']
        # Momentum = 1Y + 6M + 3M (Max 20)
        mom_score = final_score_row['Score_Mom1Y'] + final_score_row['Score_Mom6M'] + final_score_row['Score_Mom3M']
        
        stats_bar = {
            "trend": 0, # Placeholder or map from Growth?
            "volume": int(final_score_row['Score_Vol'] * 10), # Vol Score is max 10, scale to 100?
            "momentum": int(mom_score * 5),
            "impact": int(val_score * 4) # Value score max 25 -> 100
        }
        # Mapping "Trend" to Growth/Profit combination?
        stats_bar['trend'] = int((growth_score + prof_score) / 45 * 100)
        
        # Generate Briefing
        ai_briefing = generate_ai_briefing(stats_bar, levels, current_price, context)
        
        return {
            "stats_bar": stats_bar,
            "signals": signals,
            "levels": levels,
            "ai_briefing": ai_briefing,
            "current_price": current_price,
            "change_pct": (current_price - prev_close)/prev_close * 100
        }
        
    except Exception as e:
        # print(f"Error context {ticker}: {e}")
        # Return fallback
        return None

def get_market_caps_bulk(tickers):
    """
    Fetch market cap for all tickers using yfinance .info (threaded).
    Returns: Dict {ticker: market_cap}
    """
    print(f"💰 Fetching Market Caps for {len(tickers)} tickers via yfinance...")
    mcaps = {}
    
    import concurrent.futures
    
    def fetch_mcap(t):
        try:
            yf_t = t.replace('.', '-')
            if t == 'BRK.B': yf_t = 'BRK-B'
            return t, yf.Ticker(yf_t).info.get('marketCap', 0)
        except:
            return t, 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(fetch_mcap, t): t for t in tickers}
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            t, mcap = future.result()
            mcaps[t] = mcap
            if i % 50 == 0:
                print(f"   Getting Market Caps... [{i}/{len(tickers)}]", end='\r')
            
    print("\n✓ Market Cap fetch complete.")
    return mcaps

def main():
    print("🚀 Fetching S&P 500 Stock Data (v1.1 Sector Relative Logic)")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Load Financials
    print("📂 Loading Financial Data...")
    try:
        if not os.path.exists('data/financials.csv'):
            print("❌ data/financials.csv not found! Please run mining script first.")
            return
        df_fin = pd.read_csv('data/financials.csv')
        print(f"✓ Loaded {len(df_fin)} financial records")
    except Exception as e:
        print(f"❌ Error loading financials: {e}")
        return

    # 2. Fetch Price History (Bulk)
    print(f"📊 Fetching Price Data for {len(SP500_TICKERS)} tickers...")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=400) # Need > 1 year for 12M Return
    
    all_hist_list = []
    
    # Using TQDM if available, else standard print
    for idx, ticker in enumerate(SP500_TICKERS, 1):
        try:
            if idx % 50 == 0: print(f"   [{idx}/{len(SP500_TICKERS)}] Fetched...")
            
            fetch_ticker = FETCH_MAP.get(ticker, ticker)
            hist = fdr.DataReader(fetch_ticker, start_date, end_date)
            
            if hist.empty or len(hist) < 260: # Need at least ~1 year
                continue
                
            hist['Ticker'] = ticker
            # Keep only necessary columns to save memory
            hist = hist[['Ticker', 'Open', 'High', 'Low', 'Close', 'Volume']]
            hist.index.name = 'Date'
            hist = hist.reset_index()
            
            all_hist_list.append(hist)
            
        except Exception as e:
            continue
            
    if not all_hist_list:
        print("❌ No price data fetched.")
        return
        
    df_all_price = pd.concat(all_hist_list)
    print(f"✓ Fetched {len(df_all_price)} total rows.")
    
    # 3. Calculate Technicals (Bulk)
    df_all_price = calculate_technical_factors_bulk(df_all_price)
    
    # 4. Score Logic (Sector Relative) - Only for Latest Date
    print("🏆 calculating Scores (Sector Ranking)...")
    latest_date = df_all_price['Date'].max()
    # Find the max date that covers most stocks?
    # Some stocks might have data for today, some yesterday.
    # Safe bet: Take Max Date.
    print(f"   Target Date: {latest_date.date()}")
    
    df_latest = df_all_price[df_all_price['Date'] == latest_date].copy()
    
    ranked_df = apply_masks_and_score_bulk(df_latest, df_fin)
    
    # 5. Fetch Market Caps (New Step)
    market_caps = get_market_caps_bulk(ranked_df['Ticker'].tolist())
    
    # 6. Generate Final JSON Output
    print("📝 Generating Final JSON...")
    
    # Load Yesterday's ranks
    yesterday_ranks = {}
    if os.path.exists('yesterday_ranks.json'):
         with open('yesterday_ranks.json', 'r', encoding='utf-8') as f:
            yesterday_ranks = json.load(f)

    final_results = []
    
    # Optimization: Create a dict of dataframes for fast history lookup
    ticker_dfs = {x: y for x, y in df_all_price.groupby('Ticker')}
    
    for idx, row in ranked_df.iterrows():
        ticker = row['Ticker']
        hist = ticker_dfs.get(ticker)
        
        if hist is None: continue
        
        # Generate Context
        ctx = analyze_single_stock_context(ticker, hist, row)
        if not ctx: continue
        
        # Metadata
        name = STOCK_NAMES.get(ticker, ticker)
        
        # Use Sector Map to get Korean Name
        raw_sector = row['Sector']
        sector_kr = SECTOR_MAP.get(raw_sector, raw_sector)
        exchange = REAL_EXCHANGES.get(ticker, "NASDAQ")
        
        # Rank Changes
        current_rank = int(row['Rank'])
        prev_info = yesterday_ranks.get(ticker, {})
        prev_rank = prev_info.get('rank', 0)
        rank_change = (prev_rank - current_rank) if prev_rank else 0
        
        # Build Object
        item = {
            "ticker": ticker,
            "name": name,
            "name_en": ticker,
            "exchange": exchange,
            "sector": sector_kr,
            "current_price": round(ctx['current_price'], 2),
            "change_pct": round(ctx['change_pct'], 2),
            "market_cap": market_caps.get(ticker, 0), # Populated from yfinance
            "base_score": 0, # Deprecated in v1.1, used placeholder
            "bonus_score": 0, # Deprecated
            "final_score": round(row['Total_Score'], 1),
            "rank": current_rank,
            "rank_change": rank_change,
            "stats_bar": ctx['stats_bar'],
            "signals": ctx['signals'],
            "levels": ctx['levels'],
            "ai_briefing": ctx['ai_briefing'],
            "related_peers": [] # Fill later
        }
        
        # Tier logic
        # Rank is 1-based.
        total = len(ranked_df)
        pct = current_rank / total
        if pct <= 0.01: item['tier'] = "OP"
        elif pct <= 0.05: item['tier'] = 1
        elif pct <= 0.20: item['tier'] = 2
        elif pct <= 0.50: item['tier'] = 3
        elif pct <= 0.80: item['tier'] = 4
        else: item['tier'] = 5
        
        final_results.append(item)
        
    # Sort by Rank
    final_results.sort(key=lambda x: x['rank'])
    
    # 7. Sector Ranking & Peers
    # Group by sector
    by_sector = {}
    for item in final_results:
        sec = item['sector']
        if sec not in by_sector: by_sector[sec] = []
        by_sector[sec].append(item)
        
    for sec, items in by_sector.items():
        # Items sorted by rank (since final_results was sorted)
        for s_idx, item in enumerate(items):
            item['sector_rank'] = s_idx + 1
            
            # Related peers (Top 3 in same sector, excluding self)
            peers = [p for p in items if p['ticker'] != item['ticker']][:3]
            item['related_peers'] = [{"ticker": p['ticker'], "change_pct": p['change_pct']} for p in peers]
            
    # Save
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(final_results, f, indent=2, ensure_ascii=False)
        
    print(f"\n✅ Success! Saved {len(final_results)} stocks to data.json")

    # Save current ranks for tomorrow
    # Create simple dict {ticker: {rank, sector_rank}}
    snapshot = {}
    for item in final_results:
        snapshot[item['ticker']] = {
            "rank": item['rank'],
            "sector_rank": item.get('sector_rank', 0)
        }
    with open('yesterday_ranks.json', 'w', encoding='utf-8') as f:
        json.dump(snapshot, f, indent=2)

if __name__ == "__main__":
    main()
