"""
build_volume_profile.py
각 종목별 매물대(Volume Profile) 사전 계산
- price_history.csv를 읽어서 가격대별 거래량 집계
- data.json에 volume_profile 필드 추가
"""

import pandas as pd
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

def build_volume_profiles():
    """
    모든 종목의 Volume Profile을 계산하여 data.json에 추가
    """
    print("📊 Loading price history...")
    price_history = pd.read_csv(DATA_DIR / "price_history.csv")
    
    print("📁 Loading data.json...")
    with open(DATA_DIR / "data.json", "r", encoding="utf-8") as f:
        stocks = json.load(f)
    
    ticker_list = [s["ticker"] for s in stocks]
    
    print(f"🔄 Processing {len(ticker_list)} stocks...")
    
    for stock in stocks:
        ticker = stock["ticker"]
        
        # 해당 종목 데이터 필터링
        ticker_data = price_history[price_history["Ticker"] == ticker]
        
        if len(ticker_data) == 0:
            stock["volume_profile"] = None
            continue
        
        # 가격대별 거래량 집계 ($1 단위)
        buckets = {}
        for _, row in ticker_data.iterrows():
            close_val = row["Close"]
            volume = row["Volume"]
            
            # NaN 값 스킵
            if pd.isna(close_val) or pd.isna(volume):
                continue
            
            price = round(close_val)
            if price not in buckets:
                buckets[price] = 0
            buckets[price] += volume
        
        # 피크 매물대 찾기
        peak_price = max(buckets, key=buckets.get) if buckets else 0
        total_volume = sum(buckets.values())
        
        # JSON 크기 최적화: 상위 30개 가격대만 저장 (충분한 정확도)
        sorted_buckets = sorted(buckets.items(), key=lambda x: x[1], reverse=True)[:30]
        top_buckets = {str(k): v for k, v in sorted_buckets}
        
        stock["volume_profile"] = {
            "buckets": top_buckets,
            "peak_price": peak_price,
            "total_volume": int(total_volume)
        }
    
    print("💾 Saving updated data.json...")
    with open(DATA_DIR / "data.json", "w", encoding="utf-8") as f:
        json.dump(stocks, f, ensure_ascii=False, indent=2)
    
    print("✅ Volume profiles added successfully!")
    print(f"   - Total stocks processed: {len(stocks)}")
    print(f"   - Sample: {stocks[0]['ticker']} peak at ${stocks[0].get('volume_profile', {}).get('peak_price', 'N/A')}")


if __name__ == "__main__":
    build_volume_profiles()
