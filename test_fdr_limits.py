import FinanceDataReader as fdr
import time

print("=== FinanceDataReader API 제한 테스트 ===\n")

test_tickers = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", 
                "META", "TSLA", "AVGO", "AMD", "NFLX"]

print(f"총 {len(test_tickers)}개 티커로 연속 요청 테스트\n")

start_time = time.time()
success_count = 0
error_count = 0

for i, ticker in enumerate(test_tickers, 1):
    try:
        data = fdr.DataReader(ticker, '2026-01-01', '2026-01-08')
        if not data.empty:
            success_count += 1
            print(f"{i}. {ticker}: ✅ Success ({data.shape[0]} rows)")
        else:
            print(f"{i}. {ticker}: ⚠️ Empty data")
    except Exception as e:
        error_count += 1
        print(f"{i}. {ticker}: ❌ Error - {e}")
    
    # Small delay between requests
    time.sleep(0.1)

elapsed = time.time() - start_time

print(f"\n{'='*50}")
print(f"결과:")
print(f"  - 성공: {success_count}/{len(test_tickers)}")
print(f"  - 실패: {error_count}/{len(test_tickers)}")
print(f"  - 소요시간: {elapsed:.2f}초")
print(f"  - 평균 속도: {elapsed/len(test_tickers):.2f}초/티커")

print(f"\n500개 티커 예상 소요시간: {(elapsed/len(test_tickers) * 500)/60:.1f}분")

# 공식 문서나 에러 메시지 확인
print("\n" + "="*50)
print("FinanceDataReader 정보:")
print(f"버전: {fdr.__version__ if hasattr(fdr, '__version__') else 'Unknown'}")
print("\n참고: FinanceDataReader는 Yahoo Finance를 백엔드로 사용합니다.")
print("실제 제한은 Yahoo Finance의 제한에 따라 달라질 수 있습니다.")
