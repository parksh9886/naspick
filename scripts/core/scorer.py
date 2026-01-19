import pandas as pd
import numpy as np

class MarketScorer:
    """
    Handles Naspick's proprietary scoring algorithm (v2.0).
    
    Changes from v1.0:
    - Momentum: 12-1M lag (excludes last month to avoid short-term reversal)
    - NEW: Stability factor (debt ratio - lower is better)
    - NEW: Risk factor (volatility - lower is better)
    - NEW: Consensus factor (target price upside)
    
    Point Allocation (100 pts total):
    - Value: 20 pts (PER 8, PBR 4, PSR 4, EV/EBITDA 4)
    - Growth: 20 pts (Rev Growth 8, EPS Growth 12)
    - Profitability: 15 pts (ROE 8, Net Margin 3, Op Margin 4)
    - Momentum: 20 pts (12M 10, 6M 5, 3M 5) - with 1M lag
    - Stability: 5 pts (Debt Ratio - lower is better)
    - Risk: 5 pts (Volatility - lower is better)
    - Consensus: 10 pts (Target Price Upside)
    - Sentiment: 5 pts (Volume Spike)
    """

    def calculate_technical_factors_bulk(self, df):
        """Bulk calculation of technical factors used for scoring"""
        print("📈 Calculating Technical Factors (Momentum, Vol, Risk)...")
        
        # Ensure sorted
        df = df.sort_values(['Ticker', 'Date'])
        
        # Momentum with 1-month lag (exclude last 21 trading days)
        # 12-1M: from 252 days ago to 21 days ago
        df['Return_12M'] = df.groupby('Ticker')['Close'].transform(
            lambda x: x.shift(21).pct_change(periods=252-21)
        )
        df['Return_6M'] = df.groupby('Ticker')['Close'].transform(
            lambda x: x.shift(21).pct_change(periods=126-21)
        )
        df['Return_3M'] = df.groupby('Ticker')['Close'].transform(
            lambda x: x.shift(21).pct_change(periods=63-21)
        )
        
        # Volume Spike: Current Vol / 3M Avg Vol
        df['Vol_3M_Avg'] = df.groupby('Ticker')['Volume'].transform(lambda x: x.rolling(window=63).mean())
        df['Vol_Spike'] = df['Volume'] / df['Vol_3M_Avg']
        
        # Risk: 60-day volatility (standard deviation of daily returns)
        df['Daily_Return'] = df.groupby('Ticker')['Close'].pct_change()
        df['Volatility_60D'] = df.groupby('Ticker')['Daily_Return'].transform(
            lambda x: x.rolling(window=60).std() * np.sqrt(252)  # Annualized
        )
        
        return df

    def apply_sector_scoring(self, daily_df, financial_map, consensus_data=None):
        """
        Apply Sector Relative Scoring (v2.0 with new factors)
        Returns scored and ranked DataFrame with 'Total_Score' and 'Rank'
        """
        if consensus_data is None:
            consensus_data = {}
            
        # Merge financials
        merged = daily_df.merge(financial_map, on='Ticker', how='left')
        
        # Filter unknown sectors
        merged = merged.dropna(subset=['Sector'])
        
        # Add consensus upside from consensus_data
        def get_upside(ticker):
            cons = consensus_data.get(ticker, {})
            if not cons:
                return np.nan
            target = cons.get('target_price', {})
            if not target:
                return np.nan
            mean_target = target.get('mean')
            if not mean_target:
                return np.nan
            # Get current price from merged df
            current = merged.loc[merged['Ticker'] == ticker, 'Close'].values
            if len(current) == 0 or current[0] <= 0:
                return np.nan
            return ((mean_target - current[0]) / current[0]) * 100
        
        merged['Consensus_Upside'] = merged['Ticker'].apply(get_upside)
        
        # Add debt ratio from consensus financial_health
        def get_debt_ratio(ticker):
            cons = consensus_data.get(ticker, {})
            fh = cons.get('financial_health', {})
            if not fh:
                return np.nan
            return fh.get('debt_ratio', np.nan)
        
        merged['Debt_Ratio'] = merged['Ticker'].apply(get_debt_ratio)
        
        # 1. Mask Negative Valuations (Give them NaN so they rank poorly)
        val_cols = ['PER', 'PBR', 'EV_EBITDA', 'PSR']
        for col in val_cols:
            if col in merged.columns:
                merged[col] = merged[col].apply(lambda x: x if x > 0 else np.nan)
        
        # 2. Sector Relative Ranking (0.0 to 1.0)
        
        # A. Value (20 pts) - Low is Good
        merged['Score_PER'] = (1 - merged.groupby('Sector')['PER'].rank(pct=True, ascending=True)) * 8
        merged['Score_PBR'] = (1 - merged.groupby('Sector')['PBR'].rank(pct=True, ascending=True)) * 4
        merged['Score_PSR'] = (1 - merged.groupby('Sector')['PSR'].rank(pct=True, ascending=True)) * 4
        merged['Score_EVEB'] = (1 - merged.groupby('Sector')['EV_EBITDA'].rank(pct=True, ascending=True)) * 4
        
        # B. Growth (20 pts) - High is Good
        merged['Score_RevG'] = merged.groupby('Sector')['Rev_Growth'].rank(pct=True, ascending=True) * 8
        merged['Score_EPSG'] = merged.groupby('Sector')['EPS_Growth'].rank(pct=True, ascending=True) * 12
        
        # C. Profitability (15 pts) - High is Good
        merged['Score_ROE'] = merged.groupby('Sector')['ROE'].rank(pct=True, ascending=True) * 8
        
        if 'Profit_Margin' in merged.columns:
            merged['Score_NM'] = merged.groupby('Sector')['Profit_Margin'].rank(pct=True, ascending=True) * 3
        else:
            merged['Score_NM'] = 0
            
        if 'Oper_Margin' in merged.columns:
            merged['Score_OM'] = merged.groupby('Sector')['Oper_Margin'].rank(pct=True, ascending=True) * 4
        else:
            merged['Score_OM'] = 0
            
        # D. Momentum (20 pts) - High is Good (with 1M lag)
        merged['Score_Mom1Y'] = merged.groupby('Sector')['Return_12M'].rank(pct=True, ascending=True) * 10
        merged['Score_Mom6M'] = merged.groupby('Sector')['Return_6M'].rank(pct=True, ascending=True) * 5
        merged['Score_Mom3M'] = merged.groupby('Sector')['Return_3M'].rank(pct=True, ascending=True) * 5
        
        # E. Stability (5 pts) - Low Debt is Good
        merged['Score_Stability'] = (1 - merged.groupby('Sector')['Debt_Ratio'].rank(pct=True, ascending=True)) * 5
        
        # F. Risk (5 pts) - Low Volatility is Good
        merged['Score_Risk'] = (1 - merged.groupby('Sector')['Volatility_60D'].rank(pct=True, ascending=True)) * 5
        
        # G. Consensus (10 pts) - High Upside is Good
        merged['Score_Consensus'] = merged.groupby('Sector')['Consensus_Upside'].rank(pct=True, ascending=True) * 10
        
        # H. Sentiment (5 pts) - High is Good (Volume Spike)
        merged['Score_Vol'] = merged.groupby('Sector')['Vol_Spike'].rank(pct=True, ascending=True) * 5
        
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

