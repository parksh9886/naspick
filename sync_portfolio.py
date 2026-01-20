import json
import datetime

# Configuration
FINAL_VALUE = 314207.0
CASH_RATIO = 0.10
EQUITY_RATIO = 0.90
TOP_N = 10

def update_portfolio_state():
    print("🔄 Generating synced portfolio_state.json...")
    
    # 1. Load Data
    try:
        with open('data/data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ data.json not found!")
        return

    # 2. Get Top 10 Stocks
    top_stocks = sorted(data, key=lambda x: x['rank'])[:TOP_N]
    print(f"📋 Top {TOP_N} Stocks: {[s['ticker'] for s in top_stocks]}")
    
    # 3. Allocate Capital
    equity_capital = FINAL_VALUE * EQUITY_RATIO
    cash_capital = FINAL_VALUE * CASH_RATIO
    per_stock_capital = equity_capital / TOP_N
    
    holdings = {}
    total_spent = 0
    
    for s in top_stocks:
        ticker = s['ticker']
        price = s.get('current_price', 0)
        
        if price > 0:
            qty = int(per_stock_capital / price)
            cost = qty * price
            holdings[ticker] = qty
            total_spent += cost
            print(f"   - Buy {ticker}: {qty} shares @ ${price:.2f} = ${cost:.2f}")
    
    # Adjust cash with remaining dust
    final_cash = cash_capital + (equity_capital - total_spent)
    final_total_value = total_spent + final_cash
    
    print(f"💰 Allocated Stocks: ${total_spent:.2f}")
    print(f"💰 Final Cash:      ${final_cash:.2f}")
    print(f"💰 Total Value:     ${final_total_value:.2f}")
    
    # 4. Save portfolio_state.json
    state = {
        "last_update": datetime.datetime.now().strftime("%Y-%m-%d"),
        "cash": round(final_cash, 2),
        "total_value": round(final_total_value, 2),
        "holdings": holdings,
        "note": f"Synced with Backtest v2.0 Result (+214.2%) on {datetime.datetime.now().strftime('%Y-%m-%d')}"
    }
    
    with open('data/portfolio_state.json', 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2)
        
    print("✅ data/portfolio_state.json updated successfully!")

if __name__ == "__main__":
    update_portfolio_state()
