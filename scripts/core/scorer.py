import pandas as pd
import numpy as np

class MarketScorer:
    """
    Handles Naspick's proprietary scoring algorithm.
    - Bulk Technical Factors (Momentum, Volume Spike)
    - Sector Relative Ranking (Value, Growth, Profit, etc.)
    - Final Score & Tier Calculation
    """

    def calculate_technical_factors_bulk(self, df):
        """Bulk calculation of technical factors used for scoring"""
        print("📈 Calculating Technical Factors (Momentum & Vol)...")
        
        # Ensure sorted
        df = df.sort_values(['Ticker', 'Date'])
        
        # Returns (Momentum)
        # Using 'fill_method=None' to avoid future warnings
        df['Return_12M'] = df.groupby('Ticker')['Close'].pct_change(periods=252, fill_method=None)
        df['Return_6M'] = df.groupby('Ticker')['Close'].pct_change(periods=126, fill_method=None)
        df['Return_3M'] = df.groupby('Ticker')['Close'].pct_change(periods=63, fill_method=None)
        
        # Volume Spike: Current Vol / 3M Avg Vol
        df['Vol_3M_Avg'] = df.groupby('Ticker')['Volume'].transform(lambda x: x.rolling(window=63).mean())
        df['Vol_Spike'] = df['Volume'] / df['Vol_3M_Avg']
        
        return df

    def apply_sector_scoring(self, daily_df, financial_map):
        """
        Apply Sector Relative Scoring (The Core Logic)
        Returns scored and ranked DataFrame with 'Total_Score' and 'Rank'
        """
        # Merge financials
        merged = daily_df.merge(financial_map, on='Ticker', how='left')
        
        # Filter unknown sectors
        merged = merged.dropna(subset=['Sector'])
        
        # 1. Mask Negative Valuations (Give them NaN so they rank poorly)
        val_cols = ['PER', 'PBR', 'EV_EBITDA', 'PSR']
        for col in val_cols:
            if col in merged.columns:
                merged[col] = merged[col].apply(lambda x: x if x > 0 else np.nan)
        
        # 2. Sector Relative Ranking (0.0 to 1.0)
        
        # A. Value (25 pts) - Low is Good
        merged['Score_PER'] = (1 - merged.groupby('Sector')['PER'].rank(pct=True, ascending=True)) * 10
        merged['Score_PBR'] = (1 - merged.groupby('Sector')['PBR'].rank(pct=True, ascending=True)) * 5
        merged['Score_PSR'] = (1 - merged.groupby('Sector')['PSR'].rank(pct=True, ascending=True)) * 5
        merged['Score_EVEB'] = (1 - merged.groupby('Sector')['EV_EBITDA'].rank(pct=True, ascending=True)) * 5
        
        # B. Growth (25 pts) - High is Good
        merged['Score_RevG'] = merged.groupby('Sector')['Rev_Growth'].rank(pct=True, ascending=True) * 10
        merged['Score_EPSG'] = merged.groupby('Sector')['EPS_Growth'].rank(pct=True, ascending=True) * 15
        
        # C. Profitability (20 pts) - High is Good
        merged['Score_ROE'] = merged.groupby('Sector')['ROE'].rank(pct=True, ascending=True) * 10
        
        if 'Profit_Margin' in merged.columns:
            merged['Score_NM'] = merged.groupby('Sector')['Profit_Margin'].rank(pct=True, ascending=True) * 5
        else:
            merged['Score_NM'] = 0
            
        if 'Oper_Margin' in merged.columns:
            merged['Score_OM'] = merged.groupby('Sector')['Oper_Margin'].rank(pct=True, ascending=True) * 5
        else:
            merged['Score_OM'] = 0
            
        # D. Momentum (20 pts) - High is Good
        merged['Score_Mom1Y'] = merged.groupby('Sector')['Return_12M'].rank(pct=True, ascending=True) * 10
        merged['Score_Mom6M'] = merged.groupby('Sector')['Return_6M'].rank(pct=True, ascending=True) * 5
        merged['Score_Mom3M'] = merged.groupby('Sector')['Return_3M'].rank(pct=True, ascending=True) * 5
        
        # E. Sentiment (10 pts) - High is Good (Volume Spike)
        merged['Score_Vol'] = merged.groupby('Sector')['Vol_Spike'].rank(pct=True, ascending=True) * 10
        
        # 3. Fill NaNs with 0
        score_cols = [c for c in merged.columns if c.startswith('Score_')]
        merged[score_cols] = merged[score_cols].fillna(0)
        
        # 4. Total Score
        merged['Total_Score'] = merged[score_cols].sum(axis=1)
        
        # Final Rank
        merged['Rank'] = merged['Total_Score'].rank(ascending=False, method='min')
        
        return merged

    def assign_tier(self, rank, total_count):
        """Calculate Tier based on Rank percentile"""
        pct = rank / total_count
        if pct <= 0.05: return 1
        elif pct <= 0.20: return 2
        elif pct <= 0.50: return 3
        elif pct <= 0.80: return 4
        else: return 5
