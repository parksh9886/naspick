import json
import os
import yfinance as yf
from datetime import datetime
from scripts.config import PATHS

# SB1 Strategy Configuration
TOP_N = 10          # Buy stocks ranked <= 10
EXIT_RANK = 50      # Sell stocks ranked > 50
MAX_POSITIONS = 20  # Maximum number of stocks to hold
FEE_RATE = 0.0025   # 0.25% transaction fee

class PortfolioManager:
    """
    Manages Daily Portfolio Value Updates & Strategy Simulation (SB1)
    """
    
    def __init__(self):
        self.paths = PATHS
        
    def load_json(self, filepath):
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def save_json(self, filepath, data):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_spy_value(self, start_value, start_date, current_date):
        """Calculate SPY benchmark value normalized to start_value"""
        try:
            spy = yf.download('SPY', start=start_date, end=current_date, progress=False, auto_adjust=True)
            if spy.empty:
                return None
            start_price = spy['Close'].iloc[0].item()
            current_price = spy['Close'].iloc[-1].item()
            return start_value * (current_price / start_price)
        except Exception as e:
            print(f"⚠️ SPY fetch error: {e}")
            return None

    def process_corporate_actions(self, portfolio):
        """Check and process Dividends and Stock Splits"""
        print("💰 Checking for Corporate Actions (Divs & Splits)...")
        holdings = portfolio.get('holdings', {})
        if not holdings: return
        
        tickers = list(holdings.keys())
        try:
            # Fetch 5 days (actions=True returns "Dividends" and "Stock Splits")
            df = yf.download(tickers, period='5d', actions=True, auto_adjust=False, progress=False, group_by='ticker')
            
            total_div_added = 0
            if 'action_history' not in portfolio:
                portfolio['action_history'] = portfolio.get('dividend_history', []) # Migrate old key if exists
            
            def is_processed(ticker, date_str, action_type):
                for d in portfolio['action_history']:
                    if d['ticker'] == ticker and d['date'] == date_str and d.get('type') == action_type:
                        return True
                return False

            for ticker in tickers:
                # Extract Ticker DataFrame
                t_df = None
                if len(tickers) == 1:
                    t_df = df
                else:
                    if ticker in df.columns:
                        t_df = df[ticker]
                
                if t_df is not None:
                    # 1. Process Dividends
                    if 'Dividends' in t_df.columns:
                        divs = t_df['Dividends'][t_df['Dividends'] > 0]
                        for date, amount in divs.items():
                            date_str = date.strftime('%Y-%m-%d')
                            if not is_processed(ticker, date_str, 'DIVIDEND'):
                                qty = holdings[ticker]
                                cash_in = amount * qty
                                portfolio['cash'] += cash_in
                                total_div_added += cash_in
                                
                                portfolio['action_history'].append({
                                    "date": date_str, "ticker": ticker, "type": "DIVIDEND",
                                    "amount": round(cash_in, 2), "per_share": amount
                                })
                                print(f"   + Dividend: {ticker} ${cash_in:.2f} ({date_str})")

                    # 2. Process Stock Splits
                    if 'Stock Splits' in t_df.columns:
                        splits = t_df['Stock Splits'][t_df['Stock Splits'] > 0]
                        for date, ratio in splits.items():
                            date_str = date.strftime('%Y-%m-%d')
                            if not is_processed(ticker, date_str, 'SPLIT'):
                                old_qty = holdings[ticker]
                                new_qty = int(old_qty * ratio)
                                holdings[ticker] = new_qty
                                
                                portfolio['action_history'].append({
                                    "date": date_str, "ticker": ticker, "type": "SPLIT",
                                    "ratio": ratio, "old_qty": old_qty, "new_qty": new_qty
                                })
                                print(f"   ✂️ Split: {ticker} 1:{ratio} (Qty {old_qty} -> {new_qty})")

            if total_div_added > 0:
                print(f"   Total Dividends Added: ${total_div_added:.2f}")

        except Exception as e:
            print(f"⚠️ Corporate action check failed: {e}")

    def update_daily(self):
        print("📊 Daily Portfolio Value Update (Modularized)")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 1. Load portfolio state
        p_path = self.paths['PORTFOLIO_STATE']
        portfolio = self.load_json(p_path)
        if not portfolio:
            print("❌ portfolio_state.json not found!")
            return
        
        print(f"✓ Loaded portfolio state (last update: {portfolio['last_update']})")
        
        # 1.5 Process Corporate Actions (Divs & Splits)
        self.process_corporate_actions(portfolio)
        
        # 2. Load current stock data
        d_path = self.paths['OUTPUT_JSON'] # data.json
        stock_data = self.load_json(d_path)
        if not stock_data:
            print("❌ data.json not found!")
            return
        
        print(f"✓ Loaded {len(stock_data)} stocks from data.json")
        
        # Create lookup dictionaries
        price_map = {s['ticker']: s['current_price'] for s in stock_data}
        rank_map = {s['ticker']: s['rank'] for s in stock_data}
        
        # 3. Calculate current portfolio value
        holdings = portfolio.get('holdings', {})
        cash = portfolio.get('cash', 0)
        
        stock_value = 0
        for ticker, qty in holdings.items():
            if ticker in price_map:
                stock_value += qty * price_map[ticker]
            else:
                print(f"⚠️ {ticker} not found in data.json, using last known value")
        
        current_value = cash + stock_value
        prev_value = portfolio.get('total_value', current_value)
        
        print(f"💰 Current Portfolio Value: ${current_value:,.2f}")
        print(f"   Cash: ${cash:,.2f} | Stocks: ${stock_value:,.2f}")
        
        # 4. Apply SB1 Strategy Rules
        # Sell: Rank > EXIT_RANK
        to_sell = []
        for ticker in list(holdings.keys()):
            if ticker in rank_map and rank_map[ticker] > EXIT_RANK:
                to_sell.append(ticker)
        
        for ticker in to_sell:
            if ticker in price_map:
                qty = holdings[ticker]
                proceeds = qty * price_map[ticker] * (1 - FEE_RATE)
                cash += proceeds
                del holdings[ticker]
                print(f"📤 SELL {ticker} (Rank {rank_map.get(ticker, '?')}): {qty} shares @ ${price_map[ticker]:.2f}")
        
        # Buy: Rank <= TOP_N and not already holding
        open_slots = MAX_POSITIONS - len(holdings)
        if open_slots > 0:
            # Get top candidates
            candidates = [(s['ticker'], s['rank']) for s in stock_data 
                          if s['rank'] <= TOP_N and s['ticker'] not in holdings]
            candidates.sort(key=lambda x: x[1])
            
            # Recalculate equity for position sizing
            equity = cash
            for ticker, qty in holdings.items():
                if ticker in price_map:
                    equity += qty * price_map[ticker]
            
            target_position_value = equity / MAX_POSITIONS
            
            for ticker, rank in candidates[:open_slots]:
                price = price_map.get(ticker, 0)
                if price <= 0:
                    continue
                
                cost_basis = price * (1 + FEE_RATE)
                if cash > target_position_value * 0.9:
                    qty = int(target_position_value / cost_basis)
                    if qty > 0:
                        cost = qty * price * (1 + FEE_RATE)
                        cash -= cost
                        holdings[ticker] = qty
                        print(f"📥 BUY {ticker} (Rank {rank}): {qty} shares @ ${price:.2f}")
        
        # 5. Recalculate final value
        final_stock_value = sum(qty * price_map.get(t, 0) for t, qty in holdings.items())
        final_value = cash + final_stock_value
        
        print(f"✅ Final Portfolio Value: ${final_value:,.2f}")
        print(f"   Holdings: {len(holdings)} stocks | Cash: ${cash:,.2f}")
        
        # 6. Load and update chart_data.json
        c_path = self.paths['CHART_DATA']
        chart_data = self.load_json(c_path) or []
        
        if not chart_data:
            print("❌ chart_data.json not found or empty!")
            return
        
        # Get today's date
        today_str = datetime.now().strftime('%Y-%m-%d')
        
        # Check if today's data already exists
        if chart_data and chart_data[-1]['date'] == today_str:
            print(f"ℹ️ Today's data ({today_str}) already exists. Updating...")
            chart_data[-1]['sb1'] = round(final_value, 2)
        else:
            # Calculate SPY value
            spy_value = chart_data[-1].get('spy', 100000) if chart_data else 100000
            
            try:
                spy = yf.download('SPY', period='2d', progress=False, auto_adjust=True)
                if not spy.empty and len(spy) >= 2:
                    prev_spy = chart_data[-1].get('spy', 100000)
                    prev_close = spy['Close'].iloc[-2].item()
                    curr_close = spy['Close'].iloc[-1].item()
                    spy_value = prev_spy * (curr_close / prev_close)
            except Exception as e:
                print(f"⚠️ SPY update failed: {e}")
            
            new_entry = {
                "date": today_str,
                "sb1": round(final_value, 2),
                "spy": round(spy_value, 2)
            }
            chart_data.append(new_entry)
            print(f"📈 Added new data point: {new_entry}")
        
        # Save chart data
        self.save_json(c_path, chart_data)
        print(f"✓ Saved chart_data.json ({len(chart_data)} total points)")
        
        # 7. Update portfolio state
        portfolio['last_update'] = today_str
        portfolio['cash'] = round(cash, 2)
        portfolio['total_value'] = round(final_value, 2)
        portfolio['holdings'] = holdings
        
        self.save_json(p_path, portfolio)
        print(f"✓ Saved portfolio_state.json")
        
        # Summary
        change_pct = (final_value - prev_value) / prev_value * 100 if prev_value > 0 else 0
        print(f"\n📊 Summary")
        print(f"   Previous Value: ${prev_value:,.2f}")
        print(f"   Current Value:  ${final_value:,.2f}")
        print(f"   Change:         {change_pct:+.2f}%")
