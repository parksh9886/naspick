import os

files_to_remove = [
    'current_tickers.txt',
    'fdr_check.txt',
    'ticker_check_result.txt',
    'test_brk.py',
    'verify_tickers.py',
    'check_tickers_clean.py',
    'check_data.py' 
]

for f in files_to_remove:
    if os.path.exists(f):
        try:
            os.remove(f)
            print(f"Removed {f}")
        except Exception as e:
            print(f"Error removing {f}: {e}")
            
print("Cleanup complete.")
