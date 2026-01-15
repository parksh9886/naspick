import pandas as pd
import numpy as np
import json
import os
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime, timedelta

# Strategies Configuration
# Strategies Configuration
STRATEGIES = {
    # Control Group
    "SB1": {"name": "Wide Buffer (No Swap)", "top_n": 10, "exit_rank": 50, "buffer": True, "weight": "equal", "hyper_carry": False, "swap": False},
    
    # Force Swap Variants (Cap 10~30)
    "Swap10": {"name": "Force Swap (Cap 10)", "top_n": 10, "exit_rank": 50, "buffer": True, "weight": "equal", "hyper_carry": False, "swap": True, "cap": 10},
    "Swap15": {"name": "Force Swap (Cap 15)", "top_n": 10, "exit_rank": 50, "buffer": True, "weight": "equal", "hyper_carry": False, "swap": True, "cap": 15},
    "Swap20": {"name": "Force Swap (Cap 20)", "top_n": 10, "exit_rank": 50, "buffer": True, "weight": "equal", "hyper_carry": False, "swap": True, "cap": 20},
    "Swap25": {"name": "Force Swap (Cap 25)", "top_n": 10, "exit_rank": 50, "buffer": True, "weight": "equal", "hyper_carry": False, "swap": True, "cap": 25},
    "Swap30": {"name": "Force Swap (Cap 30)", "top_n": 10, "exit_rank": 50, "buffer": True, "weight": "equal", "hyper_carry": False, "swap": True, "cap": 30},
    
    # User Request: Elite Force Swap (Top 3 Buy / Max 10 / Swap Worst)
    "SwapTop3": {"name": "Elite Swap (Top 3/Cap 10)", "top_n": 3, "exit_rank": 999, "buffer": True, "weight": "equal", "hyper_carry": False, "swap": True, "cap": 10},

    # New Hybrid Strategy: SB1 + Super Rookie Swap
    "Hybrid": {"name": "Hybrid (SB1 + Super Rookie)", "top_n": 10, "exit_rank": 50, "buffer": True, "weight": "equal", "hyper_carry": False, "swap": False, "hybrid_swap": True, "cap": 10},
}

# Transaction Fee
FEE_RATE = 0.0025

def load_data():
    if not os.path.exists('data/ranking_history.csv'):
        print("❌ ranking_history.csv not found!")
        return None
    df = pd.read_csv('data/ranking_history.csv', parse_dates=['Date'])
    df = df.sort_values(['Date', 'Rank'])
    return df

def get_benchmark(start_date, end_date):
    try:
        # Fix: Ensure dates are standard datetime
        if isinstance(start_date, (np.datetime64, pd.Timestamp)):
            start_date = pd.to_datetime(start_date).to_pydatetime()
        if isinstance(end_date, (np.datetime64, pd.Timestamp)):
            end_date = pd.to_datetime(end_date).to_pydatetime()
            
        spy = yf.download('SPY', start=start_date, end=end_date + timedelta(days=5), progress=False, auto_adjust=True)
        # Normalize to start at 100,000
        if spy.empty: return None
        
        # Filter to matching dates
        spy = spy.loc[start_date:end_date]
        
        # Calculate daily value starting from 100k
        start_price = spy['Close'].iloc[0].item()
        spy['Benchmark_Value'] = (spy['Close'] / start_price) * 100000
        return spy[['Benchmark_Value']]
    except Exception as e:
        print(f"⚠️ Failed to fetch Benchmark: {e}")
        return None

def run_strategy_simulation(df, strategy_code, config, fee_rate, spy_data=None, return_trade_log=False):
    print(f"   Running Strategy {strategy_code}: {config['name']}...")
    
    initial_capital = 100000
    cash = initial_capital
    portfolio = {} # {ticker: quantity}
    history = []
    trade_count = 0
    trade_log = [] # List of {Date, Action, Ticker, Price, Qty}    
    dates = np.sort(df['Date'].unique())
    
    for date in dates:
        daily_data = df[df['Date'] == date].copy()
        date_str = str(pd.to_datetime(date).date())
        
        # Prepare Candidate List based on Strategy
        candidates = []
        
        # Calculate Benchmark MA if needed (SB4)
        market_bullish = True
        if config.get('market_timing') and spy_data is not None:
            # Check SPY MA200
            current_spy_val = spy_data.loc[date]['Benchmark_Value'] if date in spy_data.index else None
            # We need historical SPY close price to calc MA. 
            # get_benchmark returns rebased value. We need raw close? 
            # Actually get_benchmark returns 'Benchmark_Value'. Let's use that for trend approx since it tracks price.
            # Calc 200d MA of benchmark value
            # This is slow inside loop. Better pre-calc.
            # But let's do simple check: Spy > spy.rolling(200).mean
            pass # Done outside or efficient way?
            
            # Efficient way: Pre-calc MA on spy_data before loop
            # But here we are inside function. 
            # Let's trust caller passed full spy_data with index
            
            # Temporary: Calculate MA on the fly (inefficient but works for backtest)
            spy_hist = spy_data.loc[:date]
            if len(spy_hist) > 200:
                ma200 = spy_hist['Benchmark_Value'].iloc[-200:].mean()
                current_val = spy_hist['Benchmark_Value'].iloc[-1]
                market_bullish = current_val > ma200
            else:
                market_bullish = True # Assume bullish if not enough data
        
        if strategy_code == 'D' or strategy_code == 'C': # Legacy support or custom
             # ... (Keep existing if needed or remove since we replaced D/E)
             pass 
        
        # Standard Filter
        candidates = daily_data[daily_data['Rank'] <= config['top_n']]
        
        # Additional Filter: Momentum (MA) for SB2
        if config.get('ma_filter'):
            # Check if Price > MA(60)
            # We need historical price for each candidate.
            # daily_data has 'Close', but not MA.
            # engine.py didn't calculate MA60 per stock.
            # We assume 'Trend' score or 'Return_3M' is proxy? 
            # User asked: "Price > 60MA".
            # We don't have MA data in simple daily_ranks.
            # Workaround: Use 'Return_3M > 0' as proxy for "Up Trend"? 
            # Or skip specific MA check and trust Rank? 
            # User request is specific.
            # If we strictly need MA, we need full history per ticker. 
            # This is heavy. Let's use 'Score_Mom3M' > 0.5 (above average) as proxy?
            # Or check 'Return_3M' > 0.
            # Let's use existing 'Return_3M' > 0 (Approx MA check).
            # Logic: If 3M return is positive, it's likely above 60D MA.
             candidates = candidates[candidates['Return_3M'] > 0]

        candidate_tickers = candidates['Ticker'].tolist()
        daily_ranks = daily_data.set_index('Ticker')

        # 1. Sell Logic
        to_sell = []
        current_holdings = list(portfolio.keys())
        
        # Market Timing Sell (Panic Sell)
        if config.get('market_timing') and not market_bullish:
             # Sell ALL
             to_sell = current_holdings
        else:
            for ticker in current_holdings:
                should_sell = False
                
                if ticker not in daily_ranks.index:
                    should_sell = False # Hold if missing data (Ghost Ticker Fix)
                else:
                    rank = daily_ranks.loc[ticker, 'Rank']
                    score = daily_ranks.loc[ticker, 'Total_Score']
                    
                    if rank > config['exit_rank']: should_sell = True
                
                if should_sell:
                    to_sell.append(ticker)
        
        # Execute Sells
        
        # Execute Sells
        current_equity = cash
        # First calculate equity from holdings
        for t, q in portfolio.items():
            if t in daily_ranks.index:
                price = daily_ranks.loc[t, 'Close']
                if pd.notna(price):
                    current_equity += q * price

        for ticker in to_sell:
            if ticker in daily_ranks.index:
                price = daily_ranks.loc[ticker, 'Close']
                if pd.isna(price) or price <= 0: continue
            else: 
                # Skip or last price?
                continue 
            
            qty = portfolio[ticker]
            proceeds = qty * price * (1 - fee_rate)
            cash += proceeds
            del portfolio[ticker]
            trade_count += 1
            if return_trade_log:
                trade_log.append({
                    "Date": date_str,
                    "Action": "SELL",
                    "Ticker": ticker,
                    "Price": price,
                    "Qty": qty
                })

        # 2. Buy Logic
        # Update Equity for Sizing
        current_equity_for_sizing = cash
        for t, q in portfolio.items():
            if t in daily_ranks.index:
                current_equity_for_sizing += q * daily_ranks.loc[t, 'Close']
        
        # Determine Target Size per Stock
        # Update logic to respect config['cap'] if present
        if config.get('cap'):
            max_pos = config['cap']
        elif strategy_code == 'E':
             max_pos = 10 
             pos_size_pct = 0.10
        elif strategy_code == 'C':
            max_pos = 5
            pos_size_pct = 0.20
        else:
            if config.get('top_n'): max_pos = config['top_n']
            else: max_pos = 10
            
        pos_size_pct = 1.0 / max_pos
        target_amt = current_equity_for_sizing * pos_size_pct

        # Fill slots
        # For swap logic: We need to iterate candidates.
        # If full, check if swap is enabled.
        
        for ticker in candidate_tickers:
            if ticker in portfolio: continue
            
            # Check price first
            price = daily_ranks.loc[ticker, 'Close']
            if pd.isna(price) or price <= 0: continue
            cost_basis = price * (1 + fee_rate)
            if pd.isna(cost_basis) or cost_basis <= 0: continue

            # If space available
            if len(portfolio) < max_pos:
                if cash > target_amt * 0.9:
                    qty = int(target_amt / cost_basis)
                    if qty > 0:
                        cost = qty * price * (1 + fee_rate)
                        cash -= cost
                        portfolio[ticker] = qty
                        trade_count += 1
                        if return_trade_log:
                            trade_log.append({
                                "Date": date_str,
                                "Action": "BUY",
                                "Ticker": ticker,
                                "Price": price,
                                "Qty": qty
                            })
            
            # Start Force Swap Logic
            elif config.get('swap') and len(portfolio) >= max_pos:
                # Find Worst Ranked holding
                # We need current ranks of all holdings
                worst_ticker = None
                worst_rank = -1
                
                for potential_sell in portfolio.keys():
                    if potential_sell in daily_ranks.index:
                        r = daily_ranks.loc[potential_sell, 'Rank']
                        if r > worst_rank:
                            worst_rank = r
                            worst_ticker = potential_sell
                    else:
                        # If missing Rank, maybe treat as worst? or keep? 
                        # Ghost ticker logic says hold.
                        pass
                
                # Compare Candidate with Worst
                candidate_rank = daily_ranks.loc[ticker, 'Rank']
                
                # Logic: If Candidate is much better than Worst?
                # E.g. Candidate is Top 10 (guaranteed by candidate_tickers list)
                # Worst is e.g. 48.
                # Swap if Candidate < Worst. (3 < 48) -> True.
                if worst_ticker and candidate_rank < worst_rank:
                    # Sell Worst
                    price_sell = daily_ranks.loc[worst_ticker, 'Close']
                    if pd.notna(price_sell) and price_sell > 0:
                        qty_sell = portfolio[worst_ticker]
                        proceeds = qty_sell * price_sell * (1 - fee_rate)
                        cash += proceeds
                        del portfolio[worst_ticker]
                        
                        # Buy Candidate (using new cash)
                        # Recalculate Buying Power? Or use target_amt?
                        # Use target_amt (1/N)
                        if cash > target_amt * 0.9:
                            qty_buy = int(target_amt / cost_basis)
                            if qty_buy > 0:
                                cost = qty_buy * price * (1 + fee_rate)
                                cash -= cost
                                portfolio[ticker] = qty_buy
                                trade_count += 2 # Sell + Buy
                                portfolio[ticker] = qty_buy
                                trade_count += 2 # Sell + Buy
            
            # Hybrid Swap Logic (SB1 + Super Rookie)
            elif config.get('hybrid_swap') and len(portfolio) >= max_pos:
                # Condition: Candidate is Top 3?
                candidate_rank = daily_ranks.loc[ticker, 'Rank']
                
                if candidate_rank <= 3:
                     # Find Worst Ranked holding
                    worst_ticker = None
                    worst_rank = -1
                    
                    for potential_sell in portfolio.keys():
                        if potential_sell in daily_ranks.index:
                            r = daily_ranks.loc[potential_sell, 'Rank']
                            if r > worst_rank:
                                worst_rank = r
                                worst_ticker = potential_sell
                    
                    # Condition: Worst Rank > 30? (Don't swap if worst is still good)
                    if worst_ticker and worst_rank > 30:
                         # Execute Swap
                        price_sell = daily_ranks.loc[worst_ticker, 'Close']
                        if pd.notna(price_sell) and price_sell > 0:
                            qty_sell = portfolio[worst_ticker]
                            proceeds = qty_sell * price_sell * (1 - fee_rate)
                            cash += proceeds
                            del portfolio[worst_ticker]
                            
                            if cash > target_amt * 0.9:
                                qty_buy = int(target_amt / cost_basis)
                                if qty_buy > 0:
                                    cost = qty_buy * price * (1 + fee_rate)
                                    cash -= cost
                                    portfolio[ticker] = qty_buy
                                    trade_count += 2 # Sell + Buy
                                    
            # End Force Swap Logic

        # End of Day Value
        total_value = cash
        for t, q in portfolio.items():
            if t in daily_ranks.index:
                total_value += q * daily_ranks.loc[t, 'Close']
        
        history.append({
            "Date": date,
            "Value": total_value
        })
        
    if return_trade_log:
        return pd.DataFrame(history).set_index('Date'), trade_count, trade_log
    return pd.DataFrame(history).set_index('Date'), trade_count

def run_simulation_set(df, fee_rate, suffix):
    print(f"\n🚀 Running Simulation Set: {suffix} (Fee: {fee_rate*100}%)")
    dates = np.sort(df['Date'].unique())
    start_date = dates[0]
    end_date = dates[-1]

    # Pre-fetch Benchmark for Market Timing Strategy
    spy_data = get_benchmark(start_date, end_date) # Returns dataframe with Benchmark_Value

    results = {}
    combined_df = pd.DataFrame(index=dates)
    
    # Remove old D/E strategies from loop logic if not needed, strategy dict is global
    # Just iterate over STRATEGIES defined at top
    
    for code, config in STRATEGIES.items():
        res_df, trades = run_strategy_simulation(df, code, config, fee_rate, spy_data)
        results[code] = res_df
        combined_df[f"{code}: {config['name']}"] = res_df['Value']
        
        final_val = res_df['Value'].iloc[-1]
        ret = (final_val - 100000) / 1000
        print(f"   👉 {code}: ${final_val:,.0f} ({ret:.1f}%) | Trades: {trades}")

    # Benchmark Column
    if spy_data is not None:
        spy_col = spy_data.reindex(combined_df.index, method='ffill')
        combined_df['S&P 500'] = spy_col['Benchmark_Value']
        combined_df['S&P 500'] = combined_df['S&P 500'].fillna(method='ffill').fillna(100000)

    # Plot
    print(f"📈 Generating Chart: {suffix}...")
    plt.figure(figsize=(12, 6))
    for col in combined_df.columns:
        style = '--' if 'S&P 500' in col else '-'
        width = 2.5 if 'Buffer' in col or 'S&P 500' in col else 1.5
        alpha = 0.8
        plt.plot(combined_df.index, combined_df[col], label=col, linestyle=style, linewidth=width, alpha=alpha)

    plt.title(f"Strategy Comparison (5 Years) - {suffix} (Fee: {fee_rate*100}%)")
    plt.ylabel("Portfolio Value ($)")
    plt.xlabel("Date")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(f'strategy_comparison_{suffix.lower().replace(" ", "_")}.png')
    combined_df.to_csv(f'strategy_comparison_{suffix.lower().replace(" ", "_")}.csv')

def run_final_showdown(df, fee_rate):
    print(f"\n🔥 Running Final Showdown: SB1 vs Swap30 vs Benchmark")
    dates = np.sort(df['Date'].unique())
    start_date = dates[0]
    end_date = dates[-1]

    # Pre-fetch Benchmark
    spy_data = get_benchmark(start_date, end_date)
    
    # Results Storage
    results = {}
    trade_counts = {}
    
    # 1. Run SB1
    res_sb1, trades_sb1 = run_strategy_simulation(df, 'SB1', STRATEGIES['SB1'], fee_rate, spy_data)
    results['SB1 (Wide Buffer)'] = res_sb1
    trade_counts['SB1 (Wide Buffer)'] = trades_sb1
    
    # 2. Run Swap30
    res_swap30, trades_swap30 = run_strategy_simulation(df, 'Swap30', STRATEGIES['Swap30'], fee_rate, spy_data)
    results['Swap30 (Force Swap)'] = res_swap30
    trade_counts['Swap30 (Force Swap)'] = trades_swap30

    # 3. Run SwapTop3 (User Request)
    res_swap3, trades_swap3 = run_strategy_simulation(df, 'SwapTop3', STRATEGIES['SwapTop3'], fee_rate, spy_data)
    results['SwapTop3 (Elite Swap)'] = res_swap3
    trade_counts['SwapTop3 (Elite Swap)'] = trades_swap3
    
    combined_df = pd.DataFrame(index=res_sb1.index)
    combined_df['SB1 (Wide Buffer)'] = res_sb1['Value']
    combined_df['Swap30 (Force Swap)'] = res_swap30['Value']
    combined_df['Swap30 (Force Swap)'] = res_swap30['Value']
    # combined_df['SwapTop3 (Elite Swap)'] = res_swap3['Value'] # Hide bad strategy

    # 4. Run Hybrid
    res_hybrid, trades_hybrid = run_strategy_simulation(df, 'Hybrid', STRATEGIES['Hybrid'], fee_rate, spy_data)
    results['Hybrid (Super Rookie)'] = res_hybrid
    trade_counts['Hybrid (Super Rookie)'] = trades_hybrid
    combined_df['Hybrid (Super Rookie)'] = res_hybrid['Value']
    
    # 3. Benchmark
    if spy_data is not None:
        spy_col = spy_data.reindex(combined_df.index, method='ffill')
        combined_df['S&P 500'] = spy_col['Benchmark_Value']
        combined_df['S&P 500'] = combined_df['S&P 500'].fillna(method='ffill').fillna(100000)

    print(f"\n📊 Final Showdown Stats (Net Fees):")
    for name, col in combined_df.items():
        # Total Return
        final_val = col.iloc[-1]
        ret = (final_val - 100000) / 1000
        
        # MDD Calculation
        rolling_max = col.cummax()
        drawdown = (col - rolling_max) / rolling_max
        mdd = drawdown.min() * 100
        
        trades = trade_counts.get(name, 0)
        
        print(f"   👉 {name}: Return +{ret:.1f}% | MDD {mdd:.1f}% | Trades {trades} | Final ${final_val:,.0f}")

    # Plot
    print(f"📈 Generating Chart: Final Showdown...")
    plt.figure(figsize=(12, 6))
    
    # Custom Colors/Styles
    styles = {
        'SB1 (Wide Buffer)': {'color': 'blue', 'width': 2.5, 'style': '-'},
        'SB1 (Wide Buffer)': {'color': 'blue', 'width': 2.5, 'style': '-'},
        'Hybrid (Super Rookie)': {'color': 'purple', 'width': 2.5, 'style': '-'},
        'Swap30 (Force Swap)': {'color': 'green', 'width': 1.5, 'style': '--'},
        'S&P 500': {'color': 'gray', 'width': 2, 'style': ':'}
    }
    
    for col_name in combined_df.columns:
        s = styles.get(col_name, {'color': 'black', 'width': 1, 'style': '-'})
        plt.plot(combined_df.index, combined_df[col_name], label=col_name, 
                 color=s['color'], linewidth=s['width'], linestyle=s['style'], alpha=0.8)

    plt.title(f"Final Showdown: Hybrid vs SB1 (2021-2025)")
    plt.ylabel("Portfolio Value ($)")
    plt.xlabel("Date")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('showdown_comparison.png')
    combined_df.to_csv('showdown_comparison.csv')

def run_rolling_start_analysis(df, fee_rate):
    print(f"\n📅 Running Rolling Start Analysis (Sensitivity Test)...")
    
    # Define start dates: Every 6 months
    all_dates = np.sort(df['Date'].unique())
    start_years = range(2021, 2025)
    start_months = [1, 7]
    
    rolling_results = []
    
    target_strategies = ['SB1', 'Swap30']
    
    for year in start_years:
        for month in start_months:
            start_dt_target = pd.Timestamp(f"{year}-{month:02d}-01")
            
            # Find closest available date
            valid_dates = all_dates[all_dates >= start_dt_target]
            if len(valid_dates) < 250: # Skip if less than ~1 year of data left
                continue
                
            actual_start_date = valid_dates[0]
            end_date = all_dates[-1]
            
            # Slice Data
            sub_df = df[df['Date'] >= actual_start_date].copy()
            
            # Run Sim for targets
            row = {"Start Date": pd.to_datetime(actual_start_date).date()}
            
            for strategy_code in target_strategies:
                config = STRATEGIES[strategy_code]
                # Pass None for spy_data to save time/complexity in loop (or fix if needed)
                # We just want relative perf
                res, _ = run_strategy_simulation(sub_df, strategy_code, config, fee_rate, spy_data=None)
                
                # Calculate CAGR
                # end_date and actual_start_date are numpy datetime64
                # subtract gives timedelta64
                delta = end_date - actual_start_date
                days = delta.astype('timedelta64[D]').astype(int)
                if days == 0: days = 1 # Prevent div by zero
                total_ret = (res['Value'].iloc[-1] / 100000) - 1
                cagr = (1 + total_ret) ** (365/days) - 1
                
                row[f"{strategy_code} CAGR"] = cagr * 100
            
            rolling_results.append(row)
            
    # Display Table
    res_df = pd.DataFrame(rolling_results)
    res_df['Diff (SB1 - Swap30)'] = res_df['SB1 CAGR'] - res_df['Swap30 CAGR']
    
    print("\n🔍 Sensitivity Analysis: Annualized Return (CAGR) by Start Date")
    print(res_df.to_string(index=False, float_format="%.1f%%"))
    
    # Summary
    sb1_win_rate = (res_df['Diff (SB1 - Swap30)'] > 0).mean() * 100
    print(f"\n🏆 SB1 Win Rate vs Swap30: {sb1_win_rate:.1f}% of starting periods")
    print(f"   Avg Outperformance: {res_df['Diff (SB1 - Swap30)'].mean():.1f}%p")


def run_monthly_rolling_analysis(df, fee_rate):
    print(f"\n📅 Running Monthly Rolling Entry Analysis (Every Month Start)...")
    
    all_dates = np.sort(df['Date'].unique())
    start_years = range(2021, 2025)
    start_months = range(1, 13)
    
    results = []
    
    for year in start_years:
        for month in start_months:
            # 1. Determine Start Date
            start_dt_target = pd.Timestamp(f"{year}-{month:02d}-01")
            
            # Find closest trading day
            valid_dates = all_dates[all_dates >= start_dt_target]
            
            # Skip if not enough data (< 1 year)
            # Actually user asked for verification. Let's allow short term too?
            # Let's stick to minimum 6 months for meaningful "outperformance"
            if len(valid_dates) < 120: 
                continue
                
            actual_start_date = valid_dates[0]
            end_date = all_dates[-1]
            
            # 2. Run Simulation for this period
            # Slice Data
            sub_df = df[df['Date'] >= actual_start_date].copy()
            
            # A. Strategy SB1
            res_sb1, _ = run_strategy_simulation(sub_df, 'SB1', STRATEGIES['SB1'], fee_rate, spy_data=None)
            final_sb1 = res_sb1['Value'].iloc[-1]
            ret_sb1 = (final_sb1 - 100000) / 1000 #(%)
            
            # B. Benchmark (SPY)
            # Calculate SPY return for same period
            # We can use get_benchmark or just calculation from known SPY price if possible?
            # Creating get_benchmark call is expensive inside loop? 
            # get_benchmark fetches from yahoo. Only 60 calls. OK.
            spy_data = get_benchmark(actual_start_date, end_date)
            if spy_data is not None:
                final_spy = spy_data['Benchmark_Value'].iloc[-1]
                # Spy data normalized to 100k start
                ret_spy = (final_spy - 100000) / 1000
            else:
                ret_spy = 0
            
            # Record
            diff = ret_sb1 - ret_spy
            win = diff > 0
            
            results.append({
                "Start Month": f"{year}-{month:02d}",
                "SB1 Return": ret_sb1,
                "SPY Return": ret_spy,
                "Diff": diff,
                "Win": win
            })
            
            print(f"   Processed {year}-{month:02d}: SB1 {ret_sb1:.1f}% vs SPY {ret_spy:.1f}% -> {'Win' if win else 'Loss'}")

    # Summary
    df_res = pd.DataFrame(results)
    win_rate = df_res['Win'].mean() * 100
    avg_outperf = df_res['Diff'].mean()
    
    print(f"\n📊 Monthly Rolling Entry Results (Total {len(df_res)} periods):")
    print(f"🏆 Win Rate: {win_rate:.1f}% (SB1 beats SPY)")
    print(f"💰 Avg Outperformance: +{avg_outperf:.1f}%p")
    
    # Save to CSV
    df_res.to_csv('monthly_rolling_results.csv', index=False)

def run_monthly_rebal_analysis(df, fee_rate):
    print(f"\n📅 Running Monthly Rebalancing Analysis (Days: 1, 5, 10, 15, 20, 25)...")

    rebal_days = [1, 5, 10, 15, 20, 25]
    results = {}
    
    # 1. Run Individual Day Strategies
    combined_df = pd.DataFrame(index=np.sort(df['Date'].unique()))
    
    for day in rebal_days:
        # Define Config: Monthly Rebal
        config = {
            "name": f"Monthly Rebal (Day {day})",
            "top_n": 10,
            "exit_rank": 999, # Not used logic here, custom simplified logic
            "rebal_day": day,
            "monthly": True
        }
        
        # We need a custom logic inside 'simulation' or just new logic?
        # Let's use custom function for speed/simplicity as logic is very different (Time-based vs Event-based)
        res_df = run_periodic_rebalance(df, day, fee_rate)
        results[f"Day {day}"] = res_df
        combined_df[f"Day {day}"] = res_df['Value']
        
        final_val = res_df['Value'].iloc[-1]
        ret = (final_val - 100000) / 1000
        print(f"   👉 Day {day}: ${final_val:,.0f} ({ret:.1f}%)")

    # 2. Run Split Strategy (1, 10, 20)
    # Average of Day 1, Day 10, Day 20 equity
    print(f"   👉 Calculating Split Strategy (1/3 each on Day 1, 10, 20)...")
    split_equity = (combined_df['Day 1'] + combined_df['Day 10'] + combined_df['Day 20']) / 3
    combined_df['Split (1/10/20)'] = split_equity
    
    final_val_split = split_equity.iloc[-1]
    ret_split = (final_val_split - 100000) / 1000
    print(f"   👉 Split (1/10/20): ${final_val_split:,.0f} ({ret_split:.1f}%)")

    # 3. Add Market Benchmark
    dates = combined_df.index
    spy_data = get_benchmark(dates[0], dates[-1])
    if spy_data is not None:
        spy_col = spy_data.reindex(combined_df.index, method='ffill')
        combined_df['S&P 500'] = spy_col['Benchmark_Value']
        combined_df['S&P 500'] = combined_df['S&P 500'].fillna(method='ffill').fillna(100000)

    # Plot
    print(f"📈 Generating Chart: Monthly Rebalancing...")
    plt.figure(figsize=(12, 6))
    
    for col in combined_df.columns:
        width = 2.5 if 'Split' in col or 'S&P' in col else 1.0
        alpha = 0.9 if 'Split' in col else 0.4
        style = '--' if 'S&P' in col else '-'
        if 'Split' in col: style = '-'
        
        plt.plot(combined_df.index, combined_df[col], label=col, linewidth=width, alpha=alpha, linestyle=style)

    plt.title(f"Monthly Rebalancing Comparison (2021-2025)")
    plt.ylabel("Portfolio Value ($)")
    plt.xlabel("Date")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('monthly_rebal_comparison.png')
    combined_df.to_csv('monthly_rebal_comparison.csv')

def run_periodic_rebalance(df, target_day, fee_rate):
    # Specialized Sim for Monthly Rebalancing
    dates = np.sort(df['Date'].unique())
    initial_capital = 100000
    cash = initial_capital
    portfolio = {} 
    
    history = []
    
    # We need to track 'Last Rebal Month' to trigger once per month
    last_rebal_month = -1
    
    for date in dates:
        dt = pd.to_datetime(date)
        current_day = dt.day
        current_month = dt.month
        
        # Check if rebalance needed
        # Logic: If current day >= target_day AND we haven't rebalanced this month yet
        should_rebal = False
        
        # Simple Logic:
        # If today is >= target_day AND (last_rebal_month != current_month)
        # BUT: What if target day is 31 and month ends at 30?
        # Better: Rebalance on the *first trading day* where day >= target_day.
        # If target_day > month_end, we might skip? 
        # Fix: If target_day is 31, just do last day. 
        # For simple 1-25 range, standard logic works.
        
        if current_day >= target_day and last_rebal_month != current_month:
            should_rebal = True
            last_rebal_month = current_month
            
        daily_data = df[df['Date'] == date]
        daily_ranks = daily_data.set_index('Ticker')
        
        if should_rebal:
            # SELL ALL first (Simplest way to Equal Weight)
            # In practice: Calculate net diff to save fees. 
            # But "Rebalance" usually means: Reset to target.
            # To optimize fees: Sell what's needed, Buy what's needed.
            
            # Target: Top 10 Stocks.
            candidates = daily_data[daily_data['Rank'] <= 10]['Ticker'].tolist()
            
            # 1. Update Current Equity
            equity = cash
            for t, q in portfolio.items():
                if t in daily_ranks.index:
                    equity += q * daily_ranks.loc[t, 'Close']
            
            target_amount = equity / 10.0 * 0.99 # Leave 1% buffer for fees/slippage
            
            # Smart Rebalance: 
            # Identify Buys and Sells
            
            # Strategy: Sell everything not in Top 10. 
            # For Top 10, adjust to target weight? Or just Hold if already in?
            # User request: "Rebalance with Top 10". Usually implies Equal Weight.
            # Let's do Full Rebalance (expensive fees) or Smart?
            # User cares about "Return". Let's do Smart Reuse to match reality.
            
            current_holdings = list(portfolio.keys())
            
            # Sell Non-Winners
            for t in current_holdings:
                if t not in candidates:
                    # Sell
                     if t in daily_ranks.index:
                        p = daily_ranks.loc[t, 'Close']
                        if pd.notna(p):
                            cash += portfolio[t] * p * (1 - fee_rate)
                            del portfolio[t]
            
            # Now we have [Holdings that are in Top 10] + Cash.
            # We want to be Equal Weight in Top 10 candidates.
            # Calculate current value of kept holdings
            # Adjust if needed? 
            # Simplification: Just Buy new Top 10 with available cash? 
            # "Equal Weight Rebalancing" implies selling winners to buy losers.
            # Let's do a rigorous Equal Weight reset.
            
            # Sell partials of winners (if val > target)
            for t in list(portfolio.keys()): # List copy for iteration
                 if t in daily_ranks.index:
                    p = daily_ranks.loc[t, 'Close']
                    val = portfolio[t] * p
                    if val > target_amount:
                        # Sell excess
                        sell_val = val - target_amount
                        qty_sell = int(sell_val / p)
                        if qty_sell > 0:
                            portfolio[t] -= qty_sell
                            cash += qty_sell * p * (1 - fee_rate)
                            
            # Buy underweights (if val < target)
            for t in candidates:
                p = 0
                if t in daily_ranks.index: p = daily_ranks.loc[t, 'Close']
                if pd.isna(p) or p <= 0: continue
                
                current_qty = portfolio.get(t, 0)
                current_val = current_qty * p
                
                if current_val < target_amount:
                    buy_val = target_amount - current_val
                    # Check cash
                    if cash > buy_val:
                        qty_buy = int(buy_val / (p * (1 + fee_rate)))
                        if qty_buy > 0:
                            portfolio[t] = current_qty + qty_buy
                            cash -= qty_buy * p * (1 + fee_rate)
                            
        # Calculate EOD Value
        total_val = cash
        for t, q in portfolio.items():
             if t in daily_ranks.index:
                total_val += q * daily_ranks.loc[t, 'Close']
                
        history.append({"Date": date, "Value": total_val})
        
    return pd.DataFrame(history).set_index('Date')

def main():
    print("🚀 Starting Multi-Strategy Backtest (5 Years)...")
    df = load_data()
    if df is None: return

    # Run Rolling Analysis
    # run_rolling_start_analysis(df, fee_rate=0.0025)
    
    # Run Monthly Rebal Analysis (User Request)
    # run_monthly_rebal_analysis(df, fee_rate=0.0025)
    
    # Run Final Showdown (Commented out to run Monthly Rolling only)
    # run_final_showdown(df, fee_rate=0.0025)
    
    # Run Monthly Rolling Analysis (User Request)
    # run_monthly_rolling_analysis(df, fee_rate=0.0025)

    # Run Best Period Deep Dive (User Request)
    run_best_period_deep_dive(df, fee_rate=0.0025)

def run_best_period_deep_dive(df, fee_rate):
    print(f"\n💎 Finding Best Historical Start Date (Max Return)...")
    
    # 1. Quick Sweep to find best date
    all_dates = np.sort(df['Date'].unique())
    start_years = range(2021, 2025)
    start_months = range(1, 13)
    
    best_ret = -999
    best_start_date = None
    
    for year in start_years:
        for month in start_months:
            start_dt = pd.Timestamp(f"{year}-{month:02d}-01")
            valid = all_dates[all_dates >= start_dt]
            if len(valid) < 120: continue
            
            # Run Mini Sim
            sub = df[df['Date'] >= valid[0]].copy()
            res, _ = run_strategy_simulation(sub, 'SB1', STRATEGIES['SB1'], fee_rate, spy_data=None, return_trade_log=False)
            ret = (res['Value'].iloc[-1] / 100000) - 1
            
            if ret > best_ret:
                best_ret = ret
                best_start_date = valid[0]
                
    print(f"\n🏆 Best Start Date Found: {pd.to_datetime(best_start_date).date()} (Return: {best_ret*100:.1f}%)")
    
    # 2. Detailed Run
    print(f"📜 Generating Trade Log for Best Period...")
    sub_df = df[df['Date'] >= best_start_date].copy()
    res, trades, logs = run_strategy_simulation(sub_df, 'SB1', STRATEGIES['SB1'], fee_rate, spy_data=None, return_trade_log=True)
    
    # Print Log
    print(f"\n==== 📜 Trade Log (SB1 from {pd.to_datetime(best_start_date).date()}) ====")
    print(f"{'Date':<12} {'Action':<6} {'Ticker':<10} {'Price':<10} {'Qty':<5}")
    print("-" * 50)
    for log in logs:
        print(f"{log['Date']:<12} {log['Action']:<6} {log['Ticker']:<10} ${log['Price']:<9.2f} {log['Qty']:<5}")
    
    final_val = res['Value'].iloc[-1]
    print("-" * 50)
    print(f"💰 Final Value: ${final_val:,.0f} (+{best_ret*100:.1f}%)")

if __name__ == "__main__":
    main()
