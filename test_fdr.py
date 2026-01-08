import FinanceDataReader as fdr
from datetime import datetime, timedelta

print("=== FinanceDataReader Test ===\n")

try:
    # Test 1: Simple fetch
    print("Test 1: Fetching AAPL data (last 30 days)")
    df = fdr.DataReader('AAPL', '2024-12-01', '2026-01-08')
    print(f"Shape: {df.shape}")
    print(f"Empty: {df.empty}")
    
    if not df.empty:
        print("\n✓ SUCCESS! Data fetched:")
        print(df.tail())
        print(f"\nColumns: {list(df.columns)}")
        print(f"Date range: {df.index[0]} to {df.index[-1]}")
    else:
        print("\n❌ Data is empty")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50)
print("\nTest 2: Different ticker (MSFT)")
try:
    df2 = fdr.DataReader('MSFT', '2025-12-01', '2026-01-08')
    print(f"MSFT Shape: {df2.shape}, Empty: {df2.empty}")
    if not df2.empty:
        print("✓ MSFT also works!")
        print(df2.tail(3))
except Exception as e:
    print(f"❌ MSFT Error: {e}")
