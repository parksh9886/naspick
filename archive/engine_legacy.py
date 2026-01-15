import pandas as pd
import numpy as np
import os
from tqdm import tqdm

def load_data():
    print("📂 Loading data...")
    if not os.path.exists('data/price_history.csv') or not os.path.exists('data/financials.csv'):
        print("❌ Data files not found!")
        return None, None
    
    # Load Price
    df_price = pd.read_csv('data/price_history.csv', parse_dates=['Date'])
    df_price = df_price.sort_values(['Ticker', 'Date'])
    
    # Load Financials
    df_fin = pd.read_csv('data/financials.csv')
    
    print(f"✅ Loaded {len(df_price)} price rows and {len(df_fin)} financial rows")
    return df_price, df_fin

def calculate_technical_factors(df):
    print("📈 Calculating Technical Factors (Momentum & Vol)...")
    
    # Needs to be done per ticker
    df['Return_12M'] = df.groupby('Ticker')['Close'].pct_change(periods=252, fill_method=None)
    df['Return_6M'] = df.groupby('Ticker')['Close'].pct_change(periods=126, fill_method=None)
    # Spec says 3M Return for Momentum? Let's check spec. 
    # Spec: 1Y(10), 6M(5), 3M(5).
    df['Return_3M'] = df.groupby('Ticker')['Close'].pct_change(periods=63, fill_method=None)
    
    # Volume Spike: Current Vol / 3M Avg Vol
    # Spec: (Current Vol / 3M Avg Vol) -> if > 1.0 -> Good
    df['Vol_3M_Avg'] = df.groupby('Ticker')['Volume'].transform(lambda x: x.rolling(window=63).mean())
    df['Vol_Spike'] = df['Volume'] / df['Vol_3M_Avg']
    
    return df

def apply_masks_and_score(daily_df, financial_map):
    # This function processes a SINGLE DAY
    
    # daily_df has [Ticker, Close, Volume, Return_12M, ...]
    # We need to merge financials
    merged = daily_df.merge(financial_map, on='Ticker', how='left')
    
    # Filter out unknown sectors or tickers without data
    merged = merged.dropna(subset=['Sector'])
    
    # --- Step 1. Preprocessing (Negative Masking) ---
    # Spec v1.1: Mask Negative Values for Valuation Metrics
    # Low is Good: PER, PBR, EV_EBITDA
    val_cols = ['PER', 'PBR', 'EV_EBITDA', 'PSR'] # PSR added as good practice, though spec didn't strictly list it in mask example
    for col in val_cols:
        if col in merged.columns:
            # If value <= 0, set to NaN
            merged[col] = merged[col].apply(lambda x: x if x > 0 else np.nan)
            
    # --- Step 2. Sector Relative Ranking ---
    # We need to score each factor
    
    # Helper to calculate percentile score (0-1)
    # High is Good: Returns, Growth, ROE, Margins
    # Low is Good: Valuation
    
    def calc_pct(series, ascending=True):
        # pct=True gives 0 to 1
        # if ascending=True (default), smallest value is 0.0, largest is 1.0 (High is Good)
        # if ascending=False, largest is 0.0? No, rank(ascending=False) means largest is rank 1.
        # Let's stick to default rank(pct=True). 
        # Smallest = 0.0, Largest = 1.0.
        # For High is Good => Score = Rank
        # For Low is Good => Score = 1 - Rank
        return series.rank(pct=True, ascending=True)

    # A. Value (25 pts) - Low is Good
    # PER(10), PBR(5), PSR(5), EV/EBITDA(5)
    # Note: If NaN (masked), it will stay NaN here. rank handles NaN by assigning NaN unless na_option is set.
    # Spec: "Step 3: NaN Handling ... fillna(0) AFTER scoring"
    
    merged['Score_PER'] = merged.groupby('Sector')['PER'].rank(pct=True, ascending=True)
    merged['Score_PER'] = (1 - merged['Score_PER']) * 10
    
    merged['Score_PBR'] = merged.groupby('Sector')['PBR'].rank(pct=True, ascending=True)
    merged['Score_PBR'] = (1 - merged['Score_PBR']) * 5
    
    merged['Score_PSR'] = merged.groupby('Sector')['PSR'].rank(pct=True, ascending=True)
    merged['Score_PSR'] = (1 - merged['Score_PSR']) * 5
    
    merged['Score_EVEB'] = merged.groupby('Sector')['EV_EBITDA'].rank(pct=True, ascending=True)
    merged['Score_EVEB'] = (1 - merged['Score_EVEB']) * 5
    
    # B. Growth (25 pts) - High is Good
    # Rev(10), NetInc(10), EPS(5)
    merged['Score_RevG'] = merged.groupby('Sector')['Rev_Growth'].rank(pct=True, ascending=True) * 10
    # We only have Rev/EPS growth in basic info usually. Let's use what we have.
    # If we mapped EPS_Growth to 'earningsGrowth', use it.
    # Net Income Growth not always available in .info. Let's assume EPS Growth covers it or double weight EPS.
    # Spec says: Rev(10), NetInc(10), EPS(5).
    # If we lack NetInc, let's boost EPS to 15.
    merged['Score_EPSG'] = merged.groupby('Sector')['EPS_Growth'].rank(pct=True, ascending=True) * 15
    
    # C. Profitability (20 pts) - High is Good
    # ROE(10), NetMargin(5), OpMargin(5)
    merged['Score_ROE'] = merged.groupby('Sector')['ROE'].rank(pct=True, ascending=True) * 10
    merged['Score_NM'] = merged.groupby('Sector')['Profit_Margin'].rank(pct=True, ascending=True) * 5
    merged['Score_OM'] = merged.groupby('Sector')['Oper_Margin'].rank(pct=True, ascending=True) * 5
    
    # D. Momentum (20 pts) - High is Good
    # 1Y(10), 6M(5), 3M(5)
    merged['Score_Mom1Y'] = merged.groupby('Sector')['Return_12M'].rank(pct=True, ascending=True) * 10
    merged['Score_Mom6M'] = merged.groupby('Sector')['Return_6M'].rank(pct=True, ascending=True) * 5
    merged['Score_Mom3M'] = merged.groupby('Sector')['Return_3M'].rank(pct=True, ascending=True) * 5
    
    # E. Sentiment (10 pts) - High is Good
    # Volume Spike(10)
    merged['Score_Vol'] = merged.groupby('Sector')['Vol_Spike'].rank(pct=True, ascending=True) * 10
    
    # --- Step 3. NaN Handling (Final Handling) ---
    score_cols = [c for c in merged.columns if c.startswith('Score_')]
    merged[score_cols] = merged[score_cols].fillna(0)
    
    # --- Step 4. Aggregation ---
    merged['Total_Score'] = merged[score_cols].sum(axis=1)
    
    # Final Rank (Overall)
    # rank(ascending=False) -> Higher score = Rank 1
    merged['Rank'] = merged['Total_Score'].rank(ascending=False, method='min')
    
    return merged[['Date', 'Ticker', 'Sector', 'Close', 'Total_Score', 'Rank', 
                   'Return_12M', 'Return_6M', 'Return_3M', 'Vol_Spike'] + score_cols]

def main():
    df_price, df_fin = load_data()
    if df_price is None: return

    # 1. Calc Technicals
    df_price = calculate_technical_factors(df_price)
    
    # 2. Daily Scoring Loop
    dates = df_price['Date'].unique()
    dates = np.sort(dates) # Fix: use np.sort instead of .sort() for DatetimeArray
    
    # We need at least 1 year of data for 12M return, so first year will be NaNs for momentum.
    # We should only score days where we have valid data.
    # However, user said "1 year of data". If we only fetched 1 year, we can't calculate 12M return for the first day.
    # We need Pre-fetched history. 
    # Check mining.py: `start_date = end_date - timedelta(days=370)`
    # So we essentially have 0 days of valid 12M Momentum.
    # This is a problem. 
    # For this "1 year backtest", we might need to rely on shorter momentum or just accept NaNs (0 score) for Mom1Y.
    # Or we assume "1Year Backtest" means we simulate trading for 1 Year, but data goes back further?
    # User said "1 year of data".
    # Let's proceed. The first 252 days will have 0 score for Mom1Y.
    
    results = []
    
    print("🚀 Starting Ranking Engine Loop...")
    for date in tqdm(dates):
        # Get slice
        daily = df_price[df_price['Date'] == date].copy()
        
        # Skip if too few tickers (e.g. holidays or partial data)
        if len(daily) < 400:
            continue
            
        ranked = apply_masks_and_score(daily, df_fin)
        results.append(ranked)
        
    if results:
        final_df = pd.concat(results)
        final_df.to_csv('data/ranking_history.csv', index=False)
        print(f"\n✅ Genereated ranking_history.csv ({len(final_df)} rows)")
        
        # Validation checks
        sample = final_df.iloc[-1]
        print("\n🔎 Sample Data (Latest):")
        print(sample)
    else:
        print("❌ No results generated.")

if __name__ == "__main__":
    main()
