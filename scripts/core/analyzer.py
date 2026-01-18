import pandas as pd
import numpy as np

class TechnicalAnalyzer:
    """
    Handles all technical analysis calculations:
    - RSI, Pivot Points, Moving Averages
    - Candlestick Patterns (Hammer, Engulfing, etc.)
    - Volume Analysis
    - Context Generation for UI
    """

    @staticmethod
    def calculate_pivot_points(high, low, close):
        """Calculate pivot points (R1/R2, S1/S2)"""
        pivot = (high + low + close) / 3
        r1 = (2 * pivot) - low
        r2 = pivot + (high - low)
        s1 = (2 * pivot) - high
        s2 = pivot - (high - low)
        
        return {
            "pivot": round(pivot, 2), "r1": round(r1, 2), "r2": round(r2, 2),
            "s1": round(s1, 2), "s2": round(s2, 2)
        }

    @staticmethod
    def calculate_rsi(data, period=14):
        """Calculate RSI from dataframe"""
        # Ensure 'Close' exists
        if 'Close' not in data.columns:
            return 50

        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        # Handle division by zero
        rs = gain / loss
        rs = rs.fillna(0) # If loss is 0, rs is inf -> fillna handles? No, inf needs handling
        
        rsi = 100 - (100 / (1 + rs))
        
        # If not enough data, return 50
        if len(rsi) == 0: return 50
        return rsi.iloc[-1]

    @staticmethod
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
            return 0

        ratio = (prev_day_vol / avg_vol_20) - 1 # e.g. 0.45 for +45%
        pct_change = round(ratio * 100)
        
        return {
            "pct_change": pct_change,
            "status": "above_avg" if pct_change > 0 else "below_avg"
        }

    @staticmethod
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
                
                # 1. Hammer
                if body > 0 and lower_shadow > body * 2 and upper_shadow < body * 0.5 and c_prev < o_prev:
                    patterns_found.append({
                        "pattern": "hammer", "signal": "bullish", "date": date_str,
                        "name_kr": "망치형", "desc": "하락 추세에서 바닥 반전 신호",
                        "name_en": "Hammer", "desc_en": "Bottom reversal signal in downtrend"
                    })
                
                # 2. Shooting Star
                elif body > 0 and upper_shadow > body * 2 and lower_shadow < body * 0.5 and c_prev > o_prev:
                    patterns_found.append({
                        "pattern": "shooting_star", "signal": "bearish", "date": date_str,
                        "name_kr": "유성형", "desc": "상승 추세에서 고점 반전 신호",
                        "name_en": "Shooting Star", "desc_en": "Top reversal signal in uptrend"
                    })
                
                # 3. Bullish Engulfing
                elif c > o and c_prev < o_prev and o <= c_prev and c >= o_prev and body > body_prev:
                    patterns_found.append({
                        "pattern": "bullish_engulfing", "signal": "bullish", "date": date_str,
                        "name_kr": "상승 장악형", "desc": "강력한 매수세로 추세 반전",
                        "name_en": "Bullish Engulfing", "desc_en": "Strong buying momentum reversal"
                    })
                
                # 4. Bearish Engulfing
                elif c < o and c_prev > o_prev and o >= c_prev and c <= o_prev and body > body_prev:
                    patterns_found.append({
                        "pattern": "bearish_engulfing", "signal": "bearish", "date": date_str,
                        "name_kr": "하락 장악형", "desc": "강력한 매도세로 추세 반전",
                        "name_en": "Bearish Engulfing", "desc_en": "Strong selling momentum reversal"
                    })
                
                # 5. Morning Star
                elif (c_prev2 < o_prev2 and body_prev < abs(c_prev2 - o_prev2) * 0.3 and
                      c > o and c > (o_prev2 + c_prev2) / 2):
                    patterns_found.append({
                        "pattern": "morning_star", "signal": "bullish", "date": date_str,
                        "name_kr": "샛별형", "desc": "강력한 바닥 반전 3봉 패턴",
                        "name_en": "Morning Star", "desc_en": "Strong bottom reversal (3-bar)"
                    })
                
                # 6. Evening Star
                elif (c_prev2 > o_prev2 and body_prev < abs(c_prev2 - o_prev2) * 0.3 and
                      c < o and c < (o_prev2 + c_prev2) / 2):
                    patterns_found.append({
                        "pattern": "evening_star", "signal": "bearish", "date": date_str,
                        "name_kr": "석별형", "desc": "강력한 고점 반전 3봉 패턴",
                        "name_en": "Evening Star", "desc_en": "Strong top reversal (3-bar)"
                    })
                    
            except Exception:
                continue
        
        return patterns_found[-1] if patterns_found else None

    @staticmethod
    def generate_detailed_context(hist, rsi_value):
        """Generate analysis context (RSI status, Candle patterns)"""
        candle = TechnicalAnalyzer.detect_candle_patterns(hist)
        
        if rsi_value >= 70: rsi_status = "overbought"
        elif rsi_value <= 30: rsi_status = "oversold"
        elif rsi_value >= 50: rsi_status = "bullish"
        else: rsi_status = "bearish"
        
        rsi_data = {"value": round(rsi_value, 1), "status": rsi_status}
        volume_data = TechnicalAnalyzer.analyze_volume(hist)
        
        return {
            "candle_pattern": candle,
            "rsi": rsi_data,
            "volume": volume_data
        }
