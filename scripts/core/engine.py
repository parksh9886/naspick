import os
import json
import pandas as pd
from datetime import datetime
from scripts.core.fetcher import StockDataFetcher
from scripts.core.analyzer import TechnicalAnalyzer
from scripts.core.scorer import MarketScorer
from scripts.config import PATHS, SECTOR_TRANS_MAP

# Try import sitemap generator
try:
    from tools.generate_sitemap import generate_sitemap
except ImportError:
    try:
        from generate_sitemap import generate_sitemap
    except ImportError:
        def generate_sitemap(): print("⚠️ Sitemap generator not found")

class NaspickEngine:
    """
    The Central Engine for Naspick Backend.
    Orchestrates Data Fetching -> Analysis -> Scoring -> Saving.
    """
    
    def __init__(self):
        self.fetcher = StockDataFetcher()
        self.scorer = MarketScorer()
        self.analyzer = TechnicalAnalyzer()
        
        # Paths from Config
        self.paths = PATHS

    def load_consensus(self):
        """Load local consensus data"""
        path = self.paths['CONSENSUS_JSON']
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def load_calendar_data(self):
        """Load cached calendar data"""
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'calendar_data.json')
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: pass
        return {}

    def run(self):
        print("🚀 Naspick Engine Started (Facade Pattern Implementation)")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 1. Load Financials
        fin_path = self.paths['FINANCIAL_INFO']
        if not os.path.exists(fin_path):
            print(f"❌ {fin_path} not found! Please run mining script first.")
            return

        df_fin = pd.read_csv(fin_path)
        print(f"✓ Loaded {len(df_fin)} financial records")

        # 2. Fetch Data
        tickers = self.fetcher.get_sp500_tickers()
        print(f"📊 Fetching Price Data for {len(tickers)} tickers...")
        
        df_all_price = self.fetcher.fetch_price_history_bulk(tickers)
        if df_all_price.empty:
            print("❌ No price data fetched. Aborting.")
            return
            
        print(f"✓ Fetched {len(df_all_price)} total rows.")

        # 3. Calculate Technical Factors (Bulk)
        df_all_price = self.scorer.calculate_technical_factors_bulk(df_all_price)

        # 3.5 Load Consensus (needed for scoring)
        consensus_data = self.load_consensus()

        # 4. Score Logic (Sector Relative)
        print("🏆 Calculating Scores (Sector Ranking)...")
        latest_date = df_all_price['Date'].max()
        print(f"   Target Date: {latest_date.date()}")

        df_latest = df_all_price[df_all_price['Date'] == latest_date].copy()
        ranked_df = self.scorer.apply_sector_scoring(df_latest, df_fin, consensus_data)

        # 5. Fetch Market Caps
        market_caps = self.fetcher.get_market_caps_bulk(ranked_df['Ticker'].tolist())
        
        # 5.5 Load Calendar Data (From Cache)
        # calendar_data = self.fetcher.fetch_calendar_data_bulk(ranked_df['Ticker'].tolist()) # OLD Live Fetch
        calendar_data = self.load_calendar_data()


        # 6. Generate Context & JSON
        print("📝 Generating Final JSON...")
        
        # Load Aux Data
        yesterday_ranks = {}
        ranks_path = self.paths['RANKS_JSON']
        if os.path.exists(ranks_path):
            with open(ranks_path, 'r', encoding='utf-8') as f:
                yesterday_ranks = json.load(f)
        
        # Korean Names
        try:
            from scripts.data.sp500_korean_names import SP500_KOREAN_NAMES
            stock_names = SP500_KOREAN_NAMES
        except ImportError:
            stock_names = {}

        # English Names
        try:
            from scripts.data.sp500_english_names import SP500_ENGLISH_NAMES
            stock_names_en = SP500_ENGLISH_NAMES
        except ImportError:
            stock_names_en = {}
            
        exchange_map = self.fetcher.get_exchange_data()
        
        final_results = []
        ticker_dfs = {x: y for x, y in df_all_price.groupby('Ticker')}
        
        for idx, row in ranked_df.iterrows():
            ticker = row['Ticker']
            hist = ticker_dfs.get(ticker)
            if hist is None: continue
            
            # Generate Basic Context using Analyzer
            ctx = self.analyzer.generate_detailed_context(hist, self.analyzer.calculate_rsi(hist))
            
            # Expanded Analysis (from original Main logic)
            # Pivot
            levels = self.analyzer.calculate_pivot_points(hist['High'].iloc[-2], hist['Low'].iloc[-2], hist['Close'].iloc[-2])
            
            # Context Variables
            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2]
            
            # BB, MACD logic (Inline for now to maintain identical logic to Phase 2)
            # RSI
            rsi = self.analyzer.calculate_rsi(hist)
            
            # MACD
            exp12 = hist['Close'].ewm(span=12, adjust=False).mean()
            exp26 = hist['Close'].ewm(span=26, adjust=False).mean()
            macd = exp12 - exp26
            signal = macd.ewm(span=9, adjust=False).mean()
            macd_golden = (macd.iloc[-2] < signal.iloc[-2]) and (macd.iloc[-1] > signal.iloc[-1])
            
            # Signals List
            signals = []
            if rsi > 70: signals.append("RSI_Overbought")
            elif rsi < 30: signals.append("RSI_Oversold")
            if macd_golden: signals.append("MACD_GoldenCross")
            
            # Stats Bar (v2.0 - 6 factors for UI)
            val_score = row['Score_PER'] + row['Score_PBR'] + row['Score_PSR'] + row['Score_EVEB']
            growth_score = row['Score_RevG'] + row['Score_EPSG']
            prof_score = row['Score_ROE'] + row['Score_NM'] + row['Score_OM']
            mom_score = row['Score_Mom1Y'] + row['Score_Mom6M'] + row['Score_Mom3M']
            stability_score = row.get('Score_Stability', 0)
            risk_score = row.get('Score_Risk', 0)
            consensus_score = row.get('Score_Consensus', 0)
            sentiment_score = row['Score_Vol']
            
            # score_breakdown: raw scores for each factor (for UI display)
            score_breakdown = {
                "value": round(val_score, 1),           # max 20
                "growth": round(growth_score, 1),       # max 20
                "profitability": round(prof_score, 1),  # max 15
                "momentum": round(mom_score, 1),        # max 20
                "stability": round(stability_score, 1), # max 5
                "risk": round(risk_score, 1),           # max 5
                "consensus": round(consensus_score, 1), # max 10
                "sentiment": round(sentiment_score, 1)  # max 5
            }
            
            # stats_bar: percentage values for animated bars (0-100)
            # Combine Growth + Profitability as "Fundamentals" (35pt -> 100%)
            stats_bar = {
                "fundamentals": int((growth_score + prof_score) / 35 * 100),
                "value": int(val_score / 20 * 100),
                "momentum": int(mom_score / 20 * 100),
                "stability": int(stability_score / 5 * 100),
                "risk": int(risk_score / 5 * 100),
                "consensus": int(consensus_score / 10 * 100),
                "sentiment": int(sentiment_score / 5 * 100)
            }
            
            # Build Item
            raw_sector = row['Sector']
            sector_kr = SECTOR_TRANS_MAP.get(raw_sector, raw_sector)
            
            current_rank = int(row['Rank'])
            prev_rk = yesterday_ranks.get(ticker, {}).get('rank', 0)
            
            item = {
                "ticker": ticker,
                "name": stock_names.get(ticker, ticker),
                "name_en": stock_names_en.get(ticker, ticker),
                "exchange": exchange_map.get(ticker, "NASDAQ"),
                "sector": sector_kr,
                "current_price": round(current_price, 2),
                "change_pct": round((current_price - prev_close)/prev_close * 100, 2),
                "market_cap": market_caps.get(ticker, 0),
                "final_score": round(row['Total_Score'], 1),
                "rank": current_rank,
                "rank_change": (prev_rk - current_rank) if prev_rk else 0,
                "tier": self.scorer.assign_tier(current_rank, len(ranked_df)),
                "stats_bar": stats_bar,
                "score_breakdown": score_breakdown,
                "signals": signals,
                "levels": levels,
                "technical_analysis": ctx,
                "consensus": consensus_data.get(ticker, None),
                "financial_health": consensus_data.get(ticker, {}).get('financial_health', None),
            }
            
            # Helper: Get or Calculate Calendar Data
            cal_data = calendar_data.get(ticker, {}) if calendar_data else {}
            
            # [Fix] Calculate Dividend Yield if missing (Priority: TTM > *4 Estimate)
            if cal_data and ('dividend_yield' not in cal_data or not cal_data['dividend_yield']):
                 if current_price > 0:
                     if 'dividend_ttm' in cal_data and cal_data['dividend_ttm'] > 0:
                         # Use exact TTM sum (Most accurate for all frequencies)
                         yield_val = (cal_data['dividend_ttm'] / current_price) * 100
                         cal_data['dividend_yield'] = round(yield_val, 2)
                     elif 'dividend_amount' in cal_data:
                         # Fallback: Assume quarterly (x4) if TTM missing
                         approx_yield = (cal_data['dividend_amount'] * 4 / current_price) * 100
                         cal_data['dividend_yield'] = round(approx_yield, 2)
            
            item["calendar"] = cal_data
            item["related_peers"] = []
            
            final_results.append(item)
            
        # 7. Final Polish
        final_results.sort(key=lambda x: x['rank'])
        
        # Sector Peers
        by_sector = {}
        for item in final_results:
            sec = item['sector']
            if sec not in by_sector: by_sector[sec] = []
            by_sector[sec].append(item)
            
        for sec, items in by_sector.items():
            for s_idx, item in enumerate(items):
                item['sector_rank'] = s_idx + 1
                peers = [p for p in items if p['ticker'] != item['ticker']][:3]
                item['related_peers'] = [{"ticker": p['ticker'], "change_pct": p['change_pct']} for p in peers]
        
        # Similar Score Peers (점수 유사 종목: 위 2개 + 아래 1개)
        total_count = len(final_results)
        for item in final_results:
            current_rank = item['rank']
            current_idx = current_rank - 1  # 0-indexed
            
            # 후보 인덱스 계산 (위 2개 + 아래 1개, 엣지케이스 처리)
            if current_rank == 1:
                # 1등: 아래 3개
                indices = [1, 2, 3]
            elif current_rank == 2:
                # 2등: 위 1개 + 아래 2개
                indices = [0, 2, 3]
            elif current_rank >= total_count - 1:
                # 꼴등 또는 끝에서 2번째: 위 3개
                indices = [current_idx - 3, current_idx - 2, current_idx - 1]
            else:
                # 일반 케이스: 위 2개 + 아래 1개
                indices = [current_idx - 2, current_idx - 1, current_idx + 1]
            
            # 유효 인덱스 필터링 및 데이터 추출
            similar_peers = []
            for idx in indices:
                if 0 <= idx < total_count and idx != current_idx:
                    p = final_results[idx]
                    similar_peers.append({"ticker": p['ticker'], "change_pct": p['change_pct']})
            
            item['similar_score_peers'] = similar_peers[:3]  # 최대 3개
        
        # 8. Save
        out_path = self.paths['OUTPUT_JSON']
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(final_results, f, indent=2, ensure_ascii=False)
            
        print(f"\n✅ Success! Saved {len(final_results)} stocks to {out_path}")
        

        # Save History
        self.save_history(ranked_df, latest_date)
        
        # Sitemap
        print("Running Sitemap generator...")
        generate_sitemap()

    def save_snapshot(self):
        """Save current results as yesterday_ranks.json (For Daily Snapshot)"""
        ranks_path = self.paths['RANKS_JSON']
        out_path = self.paths['OUTPUT_JSON']
        
        if not os.path.exists(out_path):
            print(f"❌ Cannot save snapshot: {out_path} not found.")
            return

        with open(out_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        snapshot = {item['ticker']: {"rank": item['rank'], "sector_rank": item.get('sector_rank',0)} for item in data}
        
        with open(ranks_path, 'w', encoding='utf-8') as f:
            json.dump(snapshot, f, indent=2)
            
        print(f"📸 Saved Daily Snapshot to {ranks_path}")

    def save_history(self, ranked_df, date):
        """Save Ranking History for charts"""
        try:
            hist_path = self.paths['RANKING_HISTORY']
            os.makedirs(os.path.dirname(hist_path), exist_ok=True)
            
            subset = ranked_df[['Ticker', 'Sector', 'Close', 'Total_Score', 'Rank']].copy()
            subset['Date'] = date
            subset = subset[['Date', 'Ticker', 'Sector', 'Close', 'Total_Score', 'Rank']]
            
            if os.path.exists(hist_path):
                old = pd.read_csv(hist_path)
                old['Date'] = pd.to_datetime(old['Date'])
                subset['Date'] = pd.to_datetime(subset['Date'])
                
                old = old[old['Date'] != date]
                final = pd.concat([old, subset], ignore_index=True)
                final = final.sort_values(['Date', 'Rank'])
            else:
                final = subset
                
            final.to_csv(hist_path, index=False)
            print(f"✓ Updated ranking history at {hist_path}")
        except Exception as e:
            print(f"❌ Error saving history: {e}")

if __name__ == "__main__":
    eng = NaspickEngine()
    eng.run()
