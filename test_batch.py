import FinanceDataReader as fdr
import time

print("=== FinanceDataReader 배치 요청 테스트 ===\n")

# Test 1: 한 번에 여러 티커 요청 가능한지?
print("Test 1: 복수 티커 동시 요청 시도")
try:
    # 일부 라이브러리는 ['AAPL', 'MSFT'] 형식 지원
    data = fdr.DataReader(['AAPL', 'MSFT'], '2026-01-01', '2026-01-08')
    print(f"✅ 배치 요청 가능! Shape: {data.shape}")
    print(data)
except Exception as e:
    print(f"❌ 배치 요청 불가능: {e}")

print("\n" + "="*50)

# Test 2: 개별 요청 - 요청 카운트 확인
print("\nTest 2: 개별 요청 (3개 티커)")
tickers = ["AAPL", "MSFT", "NVDA"]
start_time = time.time()

for ticker in tickers:
    try:
        data = fdr.DataReader(ticker, '2026-01-06', '2026-01-08')
        print(f"{ticker}: {data.shape[0]} rows")
    except Exception as e:
        print(f"{ticker}: Error - {e}")
        
elapsed = time.time() - start_time
print(f"\n소요시간: {elapsed:.2f}초")
print(f"평균 속도: {elapsed/len(tickers):.2f}초/티커")
print(f"\n계산: 500개 티커 = {(elapsed/len(tickers) * 500)/60:.1f}분 예상")

print("\n" + "="*50)
print("\n결론:")
print("- 개별 요청 필요시: 500개 × 1회 = 500회 요청")
print("- 하루 800회 제한 → 500개는 1회만 가능")
print("- 15분마다 업데이트 = 불가능 (1일 96회 × 500 = 48,000회 필요)")
