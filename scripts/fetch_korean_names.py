"""
Korean Stock Name Fetcher
Fetches official Korean names for US stocks from Naver Finance.

Usage:
    python fetch_korean_names.py
    
Output:
    Creates/updates scripts/data/sp500_korean_names_naver.py
"""

import requests
import json
import time
import re
from pathlib import Path

# Naver Finance API for US stocks
# Example: https://api.stock.naver.com/stock/TSLA/basic
NAVER_API_URL = "https://api.stock.naver.com/stock/{ticker}/basic"

# Headers to mimic browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Referer": "https://finance.naver.com/"
}

def get_sp500_tickers():
    """Load S&P 500 tickers from existing file."""
    # Read from existing Korean names file to get ticker list
    names_path = Path(__file__).parent / "data" / "sp500_korean_names.py"
    
    if names_path.exists():
        content = names_path.read_text(encoding='utf-8')
        # Extract tickers using regex
        tickers = re.findall(r'"([A-Z.]+)":\s*"', content)
        return tickers
    
    # Fallback: hardcoded major tickers
    return ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META"]


def fetch_korean_name(ticker: str) -> str | None:
    """Fetch Korean name for a single ticker from Naver Finance."""
    try:
        # Handle tickers with dots (BRK.B -> BRKB for some APIs)
        url = NAVER_API_URL.format(ticker=ticker.replace(".", ""))
        
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # Naver returns data like: {"stockName": "테슬라", "stockNameEng": "Tesla Inc", ...}
            korean_name = data.get("stockName")
            if korean_name:
                return korean_name
        
        # Try with original ticker format
        if "." in ticker:
            url = NAVER_API_URL.format(ticker=ticker)
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("stockName")
                
        return None
        
    except Exception as e:
        print(f"  Error fetching {ticker}: {e}")
        return None


def main():
    print("🔍 Fetching Korean names from Naver Finance...")
    
    tickers = get_sp500_tickers()
    print(f"  Found {len(tickers)} tickers to process")
    
    results = {}
    failed = []
    
    for i, ticker in enumerate(tickers):
        korean_name = fetch_korean_name(ticker)
        
        if korean_name:
            results[ticker] = korean_name
            print(f"  [{i+1}/{len(tickers)}] {ticker}: {korean_name}")
        else:
            failed.append(ticker)
            print(f"  [{i+1}/{len(tickers)}] {ticker}: FAILED")
        
        # Rate limiting: 0.5 second delay
        time.sleep(0.5)
    
    print(f"\n✅ Success: {len(results)} | ❌ Failed: {len(failed)}")
    
    if results:
        # Save results
        output_path = Path(__file__).parent / "data" / "sp500_korean_names_naver.py"
        
        content = "# Korean names fetched from Naver Finance\n"
        content += "# Auto-generated - do not edit manually\n\n"
        content += "NAVER_KOREAN_NAMES = {\n"
        
        for ticker, name in sorted(results.items()):
            content += f'    "{ticker}": "{name}",\n'
        
        content += "}\n"
        
        output_path.write_text(content, encoding='utf-8')
        print(f"\n💾 Saved to: {output_path}")
    
    if failed:
        print(f"\n⚠️ Failed tickers: {', '.join(failed[:20])}{'...' if len(failed) > 20 else ''}")


if __name__ == "__main__":
    main()
