import FinanceDataReader as fdr
# v1.2 - Pure FDR (yfinance removed)
import pandas as pd
import numpy as np
import json
import time
import os
from datetime import datetime, timedelta
# [SEO] Import Sitemap Generator
from generate_sitemap import generate_sitemap
import warnings
import requests
warnings.filterwarnings('ignore')

# Finnhub Configuration
FINNHUB_API_KEY = "d5joti1r01qjaedqu460d5joti1r01qjaedqu46g"  # Provided by user
FINNHUB_BASE_URL = "https://finnhub.io/api/v1"

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

def detect_candle_patterns(hist, lookback_days=5):
    """
    Detect 6 major candlestick patterns in the last N days.
    Returns: {"pattern": str, "signal": str, "date": str, "name_kr": str} or None
    """
    if len(hist) < lookback_days + 2:
        return None
    
    patterns_found = []
    
    for i in range(-lookback_days, 0):
        try:
            # Current candle
            o = hist['Open'].iloc[i]
            h = hist['High'].iloc[i]
            l = hist['Low'].iloc[i]
            c = hist['Close'].iloc[i]
            
            # Previous candle
            o_prev = hist['Open'].iloc[i-1]
            c_prev = hist['Close'].iloc[i-1]
            
            # Two days ago (for 3-candle patterns)
            o_prev2 = hist['Open'].iloc[i-2] if abs(i) < len(hist) - 2 else o_prev
            c_prev2 = hist['Close'].iloc[i-2] if abs(i) < len(hist) - 2 else c_prev
            
            body = abs(c - o)
            upper_shadow = h - max(o, c)
            lower_shadow = min(o, c) - l
            body_prev = abs(c_prev - o_prev)
            
            date_str = str(hist['Date'].iloc[i])[:10] if 'Date' in hist.columns else str(i)
            
            # 1. Hammer (하락 후 긴 아래꼬리)
            if body > 0 and lower_shadow > body * 2 and upper_shadow < body * 0.5 and c_prev < o_prev:
                patterns_found.append({
                    "pattern": "hammer", "signal": "bullish", "date": date_str,
                    "name_kr": "망치형", "desc": "하락 추세에서 바닥 반전 신호"
                })
            
            # 2. Shooting Star (상승 후 긴 윗꼬리)
            elif body > 0 and upper_shadow > body * 2 and lower_shadow < body * 0.5 and c_prev > o_prev:
                patterns_found.append({
                    "pattern": "shooting_star", "signal": "bearish", "date": date_str,
                    "name_kr": "유성형", "desc": "상승 추세에서 고점 반전 신호"
                })
            
            # 3. Bullish Engulfing
            elif c > o and c_prev < o_prev and o <= c_prev and c >= o_prev and body > body_prev:
                patterns_found.append({
                    "pattern": "bullish_engulfing", "signal": "bullish", "date": date_str,
                    "name_kr": "상승 장악형", "desc": "강력한 매수세로 추세 반전"
                })
            
            # 4. Bearish Engulfing
            elif c < o and c_prev > o_prev and o >= c_prev and c <= o_prev and body > body_prev:
                patterns_found.append({
                    "pattern": "bearish_engulfing", "signal": "bearish", "date": date_str,
                    "name_kr": "하락 장악형", "desc": "강력한 매도세로 추세 반전"
                })
            
            # 5. Morning Star (3봉 패턴)
            elif (c_prev2 < o_prev2 and body_prev < abs(c_prev2 - o_prev2) * 0.3 and
                  c > o and c > (o_prev2 + c_prev2) / 2):
                patterns_found.append({
                    "pattern": "morning_star", "signal": "bullish", "date": date_str,
                    "name_kr": "샛별형", "desc": "강력한 바닥 반전 3봉 패턴"
                })
            
            # 6. Evening Star (3봉 패턴)
            elif (c_prev2 > o_prev2 and body_prev < abs(c_prev2 - o_prev2) * 0.3 and
                  c < o and c < (o_prev2 + c_prev2) / 2):
                patterns_found.append({
                    "pattern": "evening_star", "signal": "bearish", "date": date_str,
                    "name_kr": "석별형", "desc": "강력한 고점 반전 3봉 패턴"
                })
                
        except Exception:
            continue
    
    return patterns_found[-1] if patterns_found else None


def analyze_volume(hist):
    """
    Analyze Volume vs 20-day Average
    Returns: {pct_change: +45, status: 'above_avg'}
    """
    if len(hist) < 21:
        return None
        
    # Use previous day (completed candle)
    prev_day_vol = hist['Volume'].iloc[-2]
    avg_vol_20 = hist['Volume'].iloc[-22:-2].mean()
    
    if avg_vol_20 == 0:
        return float(0)

    ratio = (prev_day_vol / avg_vol_20) - 1 # e.g. 0.45 for +45%
    pct_change = round(ratio * 100)
    
    return {
        "pct_change": pct_change,
        "status": "above_avg" if pct_change > 0 else "below_avg"
    }

def fetch_consensus_data(ticker):
    """
    Fetch Price Target and Recommendation from Finnhub
    """
    if not FINNHUB_API_KEY:
        return None
        
    try:
        # A. Price Target
        target_url = f"{FINNHUB_BASE_URL}/stock/price-target?symbol={ticker}&token={FINNHUB_API_KEY}"
        r_target = requests.get(target_url)
        target_data = r_target.json()
        
        # B. Recommendation
        rec_url = f"{FINNHUB_BASE_URL}/stock/recommendation?symbol={ticker}&token={FINNHUB_API_KEY}"
        r_rec = requests.get(rec_url)
        rec_data = r_rec.json()
        
        # Process Price Target
        # Finnhub returns {targetHigh, targetLow, targetMean, ...}
        if not target_data or 'targetMean' not in target_data or target_data['targetMean'] == 0:
            return None
            
        target_price = {
            "low": target_data.get('targetLow'),
            "mean": target_data.get('targetMean'),
            "high": target_data.get('targetHigh')
        }
        
        # Process Recommendation
        # Finnhub returns list of historical recommendations. We need the latest one.
        # Format: [{period: '2024-01-01', buy: 12, hold: 5, ...}, ...]
        if not rec_data:
            return None
            
        latest_rec = rec_data[0] # Usually sorted by date desc, but let's check
        # Sometimes finnhub returns unsorted? API docs say "latest first" usually.
        # Let's assume index 0 is latest.
        
        # Calculate Score
        # Strong Buy(5), Buy(4), Hold(3), Sell(2), Strong Sell(1)
        sb = latest_rec.get('strongBuy', 0)
        b = latest_rec.get('buy', 0)
        h = latest_rec.get('hold', 0)
        s = latest_rec.get('sell', 0)
        ss = latest_rec.get('strongSell', 0)
        
        total = sb + b + h + s + ss
        
        if total == 0:
            score = 3.0 # Default Neutral
            status = "Neutral"
        else:
            weighted_sum = (sb * 5) + (b * 4) + (h * 3) + (s * 2) + (ss * 1)
            score = round(weighted_sum / total, 1)
            
            if score >= 4.5: status = "Strong Buy"
            elif score >= 3.5: status = "Buy"
            elif score >= 2.5: status = "Hold"
            elif score >= 1.5: status = "Sell"
            else: status = "Strong Sell"
            
        return {
            "target_price": target_price,
            "recommendation": {
                "score": score,
                "status": status,
                "counts": {"strongBuy": sb, "buy": b, "hold": h, "sell": s, "strongSell": ss},
                "total": total
            }
        }
        
    except Exception as e:
        print(f"Error fetching Finnhub data for {ticker}: {e}")
        return None


def generate_technical_analysis(hist, rsi_value):
    """Generate technical analysis data replacing AI briefing."""
    candle_pattern = detect_candle_patterns(hist)
    
    if rsi_value >= 70:
        rsi_status = "overbought"
    elif rsi_value <= 30:
        rsi_status = "oversold"
    elif rsi_value >= 50:
        rsi_status = "bullish"
    else:
        rsi_status = "bearish"
    
    rsi_data = {"value": round(rsi_value, 1), "status": rsi_status}
    volume_data = analyze_volume(hist)
    
    return {
        "candle_pattern": candle_pattern,
        "rsi": rsi_data,
        "volume": volume_data
    }




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
        
        # Generate Technical Analysis (replaces AI Briefing)
        technical_analysis = generate_technical_analysis(hist, rsi)
        
        context = {
            "stats_bar": stats_bar,
            "signals": signals,
            "levels": levels,
            "technical_analysis": technical_analysis,
            "current_price": current_price,
            "change_pct": (current_price - prev_close)/prev_close * 100
        }

        # Volume Analysis
        context['volume'] = analyze_volume(hist)
        
        # [NEW] Wall Street Consensus (Finnhub)
        try:
            consensus = fetch_consensus_data(ticker)
            if consensus:
                context['consensus'] = consensus
                print(f"      + Consensus: Price Target ${consensus['target_price']['mean']}, Score {consensus['recommendation']['score']}")
            else:
                print(f"      - Consensus: No data")
        except Exception as e:
            print(f"      ! Consensus Error: {e}")
            context['consensus'] = None
        
        # Rate limiting for Finnhub (20 calls/min = 3s delay)
        time.sleep(3.1) 
        
        return context
        
    except Exception as e:
        # print(f"Error context {ticker}: {e}")
        # Return fallback
        return None

def get_market_caps_bulk(tickers):
    """
    Fetch market cap for all tickers using FinanceDataReader.
    Returns: Dict {ticker: market_cap}
    """
    print(f"💰 Fetching Market Caps for {len(tickers)} tickers via FinanceDataReader...")
    mcaps = {}
    
    try:
        # Fetch broad US market data which contains Market Cap
        # print("  - Fetching NASDAQ...")
        df_nasdaq = fdr.StockListing('NASDAQ')
        # print("  - Fetching NYSE...")
        df_nyse = fdr.StockListing('NYSE')
        # print("  - Fetching AMEX...")
        df_amex = fdr.StockListing('AMEX')
        
        combined = pd.concat([df_nasdaq, df_nyse, df_amex])
        
        # Create lookup
        col = 'MarCap' if 'MarCap' in combined.columns else 'MarketCap'
        if col in combined.columns:
            mc_lookup = dict(zip(combined['Symbol'], combined[col]))
            
            for t in tickers:
                mc = mc_lookup.get(t)
                if not mc:
                    # Try hyphenated for lookup
                    mc = mc_lookup.get(t.replace('.', '-'))
                
                if mc:
                    mcaps[t] = int(mc)
                else:
                    mcaps[t] = 0
        else:
            # If column missing, just return 0s
            pass

    except Exception as e:
        print(f"❌ Error fetching market cap data: {e}")
        return {}
            
    print(f"✓ Market Cap fetch complete. Found {len(mcaps)}/{len(tickers)}")
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
            "technical_analysis": ctx.get('technical_analysis', {}),
            "consensus": ctx.get('consensus', None), # [NEW] Consensus Data
            "related_peers": [] # Fill later
        }
        
        # Tier logic
        # Rank is 1-based.
        total = len(ranked_df)
        pct = current_rank / total
        if pct <= 0.05: item['tier'] = 1
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

    # Save ranking history for chart generation
    print("\n📊 Saving ranking history for chart data...")
    try:
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        # Create minimal ranking history needed for chart generation
        # Include Date, Ticker, Sector, Close, Total_Score, Rank
        chart_history = ranked_df[['Ticker', 'Sector', 'Close', 'Total_Score', 'Rank']].copy()
        chart_history['Date'] = latest_date
        
        # Reorder columns to match expected format
        chart_history = chart_history[['Date', 'Ticker', 'Sector', 'Close', 'Total_Score', 'Rank']]
        
        chart_history.to_csv('data/ranking_history.csv', index=False)
        print(f"✓ Saved ranking snapshot for {len(chart_history)} stocks to data/ranking_history.csv")
    except Exception as e:
        print(f"⚠️ Warning: Failed to save ranking history: {e}")


    # Update Chart Data (Incremental)
    # Instead of regenerating entire history, just append today's data point
    try:
        print("\n📊 Updating Chart Data (Incremental)...")
        
        # Load existing chart data
        chart_data = []
        if os.path.exists('chart_data.json'):
            with open('chart_data.json', 'r') as f:
                chart_data = json.load(f)
            print(f"   ✓ Loaded {len(chart_data)} existing data points")
        
        # Get today's date string
        today_str = latest_date.strftime('%Y-%m-%d')
        
        # Check if today's data already exists
        if chart_data and chart_data[-1]['date'] == today_str:
            print(f"   ℹ️ Today's data ({today_str}) already exists. Skipping update.")
        else:
            # Simple approach: Keep chart static, don't update portfolio values
            # The historical backtest data will remain as-is
            # Future enhancement: Calculate actual portfolio changes and append
            print(f"   ℹ️ Chart data remains static (historical backtest completed)")
            print(f"   ℹ️ To update with live tracking, implement portfolio value calculation")
        
        print(f"✅ Chart data current: {len(chart_data)} total points")
        
    except Exception as e:
        print(f"❌ Failed to update chart data: {e}")


if __name__ == "__main__":
    main()
    # [SEO] Generate Sitemap & Robots.txt after data update
    generate_sitemap()

