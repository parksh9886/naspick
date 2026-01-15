"""
Naspick Portfolio Viewer
현재 포트폴리오의 보유 종목과 평단가를 확인하는 스크립트
"""

import json
import pandas as pd
from datetime import datetime
from multi_backtest import load_data, run_strategy_simulation, STRATEGIES
from collections import defaultdict

def calculate_holdings_from_trades(trade_log):
    """거래 로그로부터 현재 보유 종목과 평단가를 계산"""
    holdings = {}  # {ticker: {'qty': float, 'total_cost': float, 'avg_price': float}}
    
    for trade in trade_log:
        ticker = trade['Ticker']
        action = trade['Action']
        price = trade['Price']
        qty = trade['Qty']
        
        if ticker not in holdings:
            holdings[ticker] = {'qty': 0, 'total_cost': 0, 'avg_price': 0}
        
        if action == 'BUY':
            # 매수: 수량과 총 비용 증가
            holdings[ticker]['total_cost'] += price * qty
            holdings[ticker]['qty'] += qty
            if holdings[ticker]['qty'] > 0:
                holdings[ticker]['avg_price'] = holdings[ticker]['total_cost'] / holdings[ticker]['qty']
        elif action == 'SELL':
            # 매도: 수량 감소, 평단가는 유지 (남은 수량 기준)
            holdings[ticker]['qty'] -= qty
            if holdings[ticker]['qty'] > 0:
                # 평단가 유지
                holdings[ticker]['total_cost'] = holdings[ticker]['avg_price'] * holdings[ticker]['qty']
            else:
                # 전량 매도
                holdings[ticker] = {'qty': 0, 'total_cost': 0, 'avg_price': 0}
    
    # 보유 수량이 0인 종목 제거
    holdings = {k: v for k, v in holdings.items() if v['qty'] > 0}
    
    return holdings

def view_current_portfolio():
    """현재 포트폴리오 상태를 상세하게 출력"""
    
    print("=" * 80)
    print("📊 NASPICK PORTFOLIO VIEWER")
    print("=" * 80)
    print(f"생성 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 데이터 로드 (multi_backtest.py의 load_data 사용)
    print("백테스팅 데이터 로드 중...")
    df = load_data()
    
    if df is None or df.empty:
        print("❌ 데이터 로드 실패")
        return
    
    # 시뮬레이션 실행 (Gross Return + Trade Log)
    print("시뮬레이션 실행 중 (SB1 전략)...")
    result_df, trade_count, trade_log = run_strategy_simulation(
        df,
        'SB1',
        STRATEGIES['SB1'],
        fee_rate=0.0,  # Gross Return
        return_trade_log=True  # 거래 로그 활성화
    )
    
    if result_df is None or result_df.empty:
        print("❌ 시뮬레이션 결과가 없습니다.")
        return
    
    # 마지막 날짜의 포트폴리오 상태 (result_df의 마지막 행)
    last_day = result_df.iloc[-1]
    
    print("\n" + "=" * 80)
    print("💼 포트폴리오 요약")
    print("=" * 80)
    print(f"기준일: {last_day.name.strftime('%Y-%m-%d')}")
    print(f"총 자산: ${last_day['Value']:,.2f}")
    
    # 수익률 계산
    initial_value = 100000
    first_day = result_df.iloc[0]
    total_return_pct = ((last_day['Value'] - first_day['Value']) / first_day['Value']) * 100
    print(f"총 수익률: {total_return_pct:+.2f}%")
    print(f"총 수익금: ${last_day['Value'] - first_day['Value']:+,.2f}")
    
    # 거래 로그로부터 보유 종목 계산
    print("\n거래 로그 분석 중...")
    holdings = calculate_holdings_from_trades(trade_log)
    
    if not holdings:
        print("\n⚠️  현재 보유 종목이 없습니다. (전량 현금)")
    else:
        # data.json에서 현재가와 종목명 로드
        with open('data.json', 'r', encoding='utf-8') as f:
            current_data = json.load(f)
        current_prices = {item['ticker']: item['current_price'] for item in current_data}
        stock_names = {item['ticker']: item['name'] for item in current_data}
        
        print("\n" + "=" * 80)
        print("📈 보유 종목 상세")
        print("=" * 80)
        print(f"{'종목코드':<10} {'종목명':<15} {'수량':>10} {'평단가':>12} {'현재가':>12} {'수익률':>10} {'평가액':>14}")
        print("-" * 80)
        
        holdings_list = []
        total_position_value = 0
        
        for ticker, data in holdings.items():
            qty = data['qty']
            avg_price = data['avg_price']
            current_price = current_prices.get(ticker, avg_price)
            stock_name = stock_names.get(ticker, ticker)
            
            position_value = qty * current_price
            return_pct = ((current_price - avg_price) / avg_price) * 100 if avg_price > 0 else 0
            
            holdings_list.append({
                'ticker': ticker,
                'name': stock_name,
                'qty': qty,
                'avg_price': avg_price,
                'current_price': current_price,
                'return_pct': return_pct,
                'value': position_value
            })
            
            total_position_value += position_value
        
        # 평가액 순으로 정렬
        holdings_list.sort(key=lambda x: x['value'], reverse=True)
        
        for h in holdings_list:
            print(f"{h['ticker']:<10} {h['name']:<15} {h['qty']:>10.2f} ${h['avg_price']:>11.2f} ${h['current_price']:>11.2f} {h['return_pct']:>+9.2f}% ${h['value']:>13,.2f}")
        
        print("-" * 80)
        print(f"{'총 주식 평가액':<54}{'':>26}${total_position_value:>13,.2f}")
        
        # 비중 분석
        print("\n" + "=" * 80)
        print("📊 포트폴리오 비중")
        print("=" * 80)
        
        for h in holdings_list:
            weight = (h['value'] / last_day['Value']) * 100
            bar_length = int(weight / 2)  # 50% = 25칸
            bar = "█" * bar_length
            
            print(f"{h['ticker']:<6} {h['name']:<12} {weight:>6.2f}% {bar}")
        
        cash_value = last_day['Value'] - total_position_value
        cash_weight = (cash_value / last_day['Value']) * 100
        bar_length = int(cash_weight / 2)
        bar = "░" * bar_length
        print(f"{'CASH':<6} {'현금':<12} {cash_weight:>6.2f}% {bar}")
    
    # 수익률 그래프 (간단한 텍스트 차트)
    print("\n" + "=" * 80)
    print("📈 포트폴리오 가치 추이 (마지막 30일)")
    print("=" * 80)
    
    recent_30 = result_df.tail(30)
    for idx, row in recent_30.iterrows():
        date_str = idx.strftime('%Y-%m-%d')
        value = row['Value']
        bar_length = int((value / 150000) * 50)  # Scale to 50 chars at 150k
        bar = "█" * bar_length
        pct = ((value - 100000) / 100000) * 100
        print(f"{date_str} ${value:>10,.0f} ({pct:>+6.2f}%) {bar}")
    
    print("\n" + "=" * 80)
    print("ℹ️  참고사항")
    print("=" * 80)
    print("- 본 포트폴리오는 SB1 전략 백테스팅 시뮬레이션 결과입니다")
    print("- 평단가는 거래 로그를 분석하여 계산됩니다")
    print("- Gross Return (수수료 미반영) 기준입니다")
    print(f"- 총 {len(trade_log)} 건의 거래가 발생했습니다")
    print("\n" + "=" * 80)
    print("✅ 포트폴리오 조회 완료")
    print("=" * 80)

if __name__ == "__main__":
    view_current_portfolio()
