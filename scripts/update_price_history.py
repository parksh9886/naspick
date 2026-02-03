"""
update_price_history.py
Rolling 180-day Price History 유지 스크립트

- 매일 Daily Snapshot 시점에 실행
- 당일 종가 데이터를 price_history.csv에 추가
- 180일보다 오래된 데이터 자동 삭제
"""

import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timedelta
from pathlib import Path
import time

DATA_DIR = Path(__file__).parent.parent / "data"
HISTORY_FILE = DATA_DIR / "price_history.csv"
ROLLING_DAYS = 180  # 180일치만 유지


def get_sp500_tickers():
    """S&P 500 티커 목록 가져오기"""
    try:
        sp500 = fdr.StockListing('SP500')
        tickers = sp500['Symbol'].tolist()
        
        # Dual class shares 정규화 (BRK-B -> BRK.B)
        required = ['BRK.B', 'BRK.A']
        for t in required:
            t_hyphen = t.replace('.', '-')
            t_concat = t.replace('.', '')
            if t_hyphen in tickers:
                tickers.remove(t_hyphen)
            if t_concat in tickers:
                tickers.remove(t_concat)
            if t not in tickers:
                tickers.append(t)
        
        return sorted(list(set(tickers)))
    except Exception as e:
        print(f"❌ Failed to get S&P 500 list: {e}")
        return []


def fetch_today_prices(tickers):
    """오늘 종가 데이터 가져오기"""
    today = datetime.now()
    # 주말/공휴일 고려하여 최근 5일치 가져와서 최신 날짜만 사용
    start = today - timedelta(days=5)
    
    all_data = []
    print(f"📊 Fetching today's closing prices for {len(tickers)} stocks...")
    
    fetch_map = {
        'BRK.B': 'BRK-B',
        'BRK.A': 'BRK-A',
    }
    
    for idx, ticker in enumerate(tickers, 1):
        if idx % 50 == 0:
            print(f"   [{idx}/{len(tickers)}] Fetched...")
            
        for attempt in range(3):
            try:
                fetch_ticker = fetch_map.get(ticker, ticker)
                df = fdr.DataReader(fetch_ticker, start, today)
                
                if df.empty:
                    if attempt < 2:
                        time.sleep(0.5)
                        continue
                    break
                
                # 가장 최근 날짜만 가져옴
                latest_row = df.iloc[-1]
                latest_date = df.index[-1]
                
                all_data.append({
                    'Date': latest_date.strftime('%Y-%m-%d'),
                    'Ticker': ticker,
                    'Close': round(latest_row['Close'], 4),
                    'Volume': int(latest_row['Volume']) if pd.notna(latest_row['Volume']) else 0
                })
                break
                
            except Exception as e:
                if attempt < 2:
                    time.sleep(0.5)
                else:
                    print(f"   ⚠️ Failed: {ticker}")
    
    if all_data:
        return pd.DataFrame(all_data)
    return pd.DataFrame()


def update_price_history():
    """
    메인 함수: price_history.csv 업데이트
    1. 기존 데이터 로드
    2. 오늘 데이터 추가
    3. 180일 초과 데이터 삭제
    4. 저장
    """
    print(f"\n📈 Updating Price History (Rolling {ROLLING_DAYS} days)")
    print(f"   Target file: {HISTORY_FILE}")
    
    # 1. 기존 데이터 로드
    if HISTORY_FILE.exists():
        existing_df = pd.read_csv(HISTORY_FILE)
        existing_df['Date'] = pd.to_datetime(existing_df['Date'])
        print(f"   ✓ Loaded existing data: {len(existing_df)} rows")
        print(f"   ✓ Date range: {existing_df['Date'].min().date()} ~ {existing_df['Date'].max().date()}")
    else:
        print("   ⚠️ No existing file found. Will create new.")
        existing_df = pd.DataFrame(columns=['Date', 'Ticker', 'Close', 'Volume'])
        existing_df['Date'] = pd.to_datetime(existing_df['Date'])
    
    # 2. 오늘 데이터 가져오기
    tickers = get_sp500_tickers()
    if not tickers:
        print("❌ No tickers found. Aborting.")
        return
        
    today_df = fetch_today_prices(tickers)
    
    if today_df.empty:
        print("❌ Failed to fetch today's data. Aborting.")
        return
    
    today_df['Date'] = pd.to_datetime(today_df['Date'])
    latest_date = today_df['Date'].iloc[0]
    print(f"   ✓ Fetched data for: {latest_date.date()} ({len(today_df)} stocks)")
    
    # 3. 중복 날짜 제거 (같은 날짜 데이터가 있으면 새 데이터로 교체)
    existing_df = existing_df[existing_df['Date'] != latest_date]
    
    # 4. 데이터 병합
    combined_df = pd.concat([existing_df, today_df], ignore_index=True)
    
    # 5. 180일보다 오래된 데이터 삭제
    cutoff_date = datetime.now() - timedelta(days=ROLLING_DAYS)
    before_count = len(combined_df)
    combined_df = combined_df[combined_df['Date'] >= cutoff_date]
    after_count = len(combined_df)
    
    if before_count > after_count:
        deleted = before_count - after_count
        print(f"   🗑️ Removed {deleted} rows older than {cutoff_date.date()}")
    
    # 6. 정렬 및 저장
    combined_df = combined_df.sort_values(['Date', 'Ticker']).reset_index(drop=True)
    combined_df['Date'] = combined_df['Date'].dt.strftime('%Y-%m-%d')
    combined_df.to_csv(HISTORY_FILE, index=False)
    
    print(f"\n✅ Price history updated successfully!")
    print(f"   📁 Saved: {len(combined_df)} rows")
    print(f"   📅 Date range: {combined_df['Date'].min()} ~ {combined_df['Date'].max()}")
    
    # 7. 간단한 통계
    unique_dates = combined_df['Date'].nunique()
    unique_tickers = combined_df['Ticker'].nunique()
    print(f"   📊 Stats: {unique_dates} trading days, {unique_tickers} stocks")


def initial_load_180_days():
    """
    초기 설정용: 180일치 데이터 한번에 로드
    (첫 실행 시 또는 데이터 초기화 필요 시 사용)
    """
    print(f"\n🔄 Initial Load: Fetching {ROLLING_DAYS} days of price history...")
    
    tickers = get_sp500_tickers()
    if not tickers:
        print("❌ No tickers found. Aborting.")
        return
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=ROLLING_DAYS + 50)  # 여유있게
    
    all_data = []
    print(f"📊 Fetching data for {len(tickers)} stocks...")
    
    fetch_map = {
        'BRK.B': 'BRK-B',
        'BRK.A': 'BRK-A',
    }
    
    for idx, ticker in enumerate(tickers, 1):
        if idx % 25 == 0:
            print(f"   [{idx}/{len(tickers)}] Fetched...")
            
        for attempt in range(3):
            try:
                fetch_ticker = fetch_map.get(ticker, ticker)
                df = fdr.DataReader(fetch_ticker, start_date, end_date)
                
                if df.empty:
                    if attempt < 2:
                        time.sleep(0.5)
                        continue
                    break
                
                # 최근 180일만 필터링
                df = df.tail(ROLLING_DAYS)
                
                for date_idx, row in df.iterrows():
                    all_data.append({
                        'Date': date_idx.strftime('%Y-%m-%d'),
                        'Ticker': ticker,
                        'Close': round(row['Close'], 4),
                        'Volume': int(row['Volume']) if pd.notna(row['Volume']) else 0
                    })
                break
                
            except Exception as e:
                if attempt < 2:
                    time.sleep(0.5)
                else:
                    print(f"   ⚠️ Failed: {ticker}")
    
    if all_data:
        result_df = pd.DataFrame(all_data)
        result_df = result_df.sort_values(['Date', 'Ticker']).reset_index(drop=True)
        result_df.to_csv(HISTORY_FILE, index=False)
        print(f"\n✅ Initial load complete!")
        print(f"   📁 Saved: {len(result_df)} rows to {HISTORY_FILE}")
    else:
        print("❌ Failed to fetch any data.")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--init":
        # 초기 로드 (180일치 전체)
        initial_load_180_days()
    else:
        # 일반 업데이트 (오늘 데이터만 추가)
        update_price_history()
