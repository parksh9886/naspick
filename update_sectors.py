import FinanceDataReader as fdr
import json
import pandas as pd

# Extended Sector Map (English -> Korean)
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

def update_sectors():
    print("🚀 Fetching reliable sector data from FinanceDataReader...")
    
    # Fetch S&P 500 listing which contains accurate Sector info
    try:
        sp500_df = fdr.StockListing('SP500')
        # Create a dictionary: Symbol -> Sector
        # Handle case where Symbol might vary slightly, but usually FDR is the source of truth
        sector_lookup = dict(zip(sp500_df['Symbol'], sp500_df['Sector']))
        
        # Manual overrides for dual class or special cases if missing
        sector_lookup['BRK.B'] = 'Financials'
        sector_lookup['BF.B'] = 'Consumer Staples'
        sector_lookup['GOOG'] = 'Communication Services'
        sector_lookup['GOOGL'] = 'Communication Services'
        sector_lookup['FOX'] = 'Communication Services'
        sector_lookup['FOXA'] = 'Communication Services'
        sector_lookup['NWS'] = 'Communication Services'
        sector_lookup['NWSA'] = 'Communication Services'

    except Exception as e:
        print(f"❌ Error fetching sector data: {e}")
        return

    print(f"✓ Loaded sector data for {len(sector_lookup)} tickers")

    # Load existing data.json
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ data.json not found")
        return

    updated_count = 0
    unknown_sectors = set()

    print("\nProcessing updates...")
    
    for item in data:
        ticker = item['ticker']
        
        # Try to find sector in lookup
        # lookup keys might not have dots for BRK/BF if they came from standard list, 
        # but we manually added dot versions above just in case.
        # Also check hyphenated version if dot version misses
        
        raw_sector = sector_lookup.get(ticker)
        if not raw_sector:
            raw_sector = sector_lookup.get(ticker.replace('.', '-'))
            
        if raw_sector:
            # Map to Korean
            korean_sector = SECTOR_MAP.get(raw_sector)
            if not korean_sector:
                korean_sector = raw_sector # Fallback to English if mapping missing
                unknown_sectors.add(raw_sector)
            
            # Update only if different
            if item.get('sector') != korean_sector:
                # print(f"  Update {ticker}: {item.get('sector')} -> {korean_sector}")
                item['sector'] = korean_sector
                updated_count += 1
        else:
            print(f"⚠ No sector data found for {ticker}")

    # Save details
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Updated sectors for {updated_count} stocks.")
    if unknown_sectors:
        print(f"⚠ Unmapped sectors found: {unknown_sectors}")
        
if __name__ == "__main__":
    update_sectors()
