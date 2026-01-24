import json
import sys

# Load data
try:
    with open(r'c:\Users\sec\Desktop\Naspick\data\data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
except Exception as e:
    print(f"Error loading data: {e}")
    sys.exit(1)

def generate_report(stock):
    name = stock.get('name', stock['ticker'])
    ticker = stock['ticker']
    score = stock.get('final_score', 0)
    tier = stock.get('tier', 3)
    sector = stock.get('sector', 'Unknown')
    
    stats = stock.get('score_breakdown', {})
    growth = stats.get('growth', 0) * 10 
    value = stats.get('value', 0) * 10
    stability = stats.get('stability', 0) * 10
    
    # Normalize stats if they are small numbers (some versions of data might be 0-10 or 0-100)
    # Based on previous view_file, score_breakdown seems to be small numbers summing to final_score?
    # Let's check stats_bar which is 0-100
    stats_bar = stock.get('stats_bar', {})
    growth_score = stats_bar.get('fundamentals', 50) # Using fundamentals as proxy for growth for now if growth specific is missing
    # Actually data.json has 'score_breakdown' with 'growth', 'value' etc. but let's see values.
    # In previous turn: "growth": 16.9 (out of ~20 max likely? or is it contribution?)
    # "stats_bar": "fundamentals": 83, "value": 63... This is 0-100. Let's use stats_bar.
    
    s_growth = stats_bar.get('fundamentals', 50) # mapping fundamentals -> growth roughly
    s_value = stats_bar.get('value', 50)
    s_stability = stats_bar.get('stability', 50)
    s_momentum = stats_bar.get('momentum', 50)
    s_risk = stats_bar.get('risk', 50) # Note: Low risk score usually means High Risk? Or High Score means Low Risk?
    # In data.json: SYF risk: 11 (Low score probably means Low Stability i.e. High Risk? or Low Volatility?)
    # Let's assume stats_bar is "Higher is Better" usually, but for Risk?
    # Actually SYF: stability 85, risk 11. 
    # Let's check logic: usually "Risk Score" in these apps: High Score = Safe? or High Score = Risky?
    # Let's infer from context. "High Risk" usually implies high volatility.
    
    consensus = stock.get('consensus', {})
    target_price = consensus.get('target_price', {})
    upside = 0
    if target_price and target_price.get('mean') and stock['current_price']:
        upside = ((target_price['mean'] - stock['current_price']) / stock['current_price']) * 100
        
    rsi = stock.get('technical_analysis', {}).get('rsi', {}).get('value', 50)
    
    # --- Generation Logic ---
    report = []
    
    # 1. Identity & Trend
    tier_str = f"{tier}티어" if tier else "분석중인"
    # --- SEO Keyword Injection ---
    # --- Generation Logic (Natural Analyst Style) ---
    report = []
    
    # Phase 1: Intro (Identity & Trend)
    # Natural phrasing: "Based on AI analysis, [Name] is currently..."
    tier_desc = "최상위권(1티어)" if tier == 1 else "상위권" if tier <= 2 else "중위권" if tier <= 3 else "하위권"
    trend_desc = "강한 상승세를 타고 있습니다" if s_momentum > 80 else "안정적인 흐름을 유지하고 있습니다" if s_momentum > 50 else "조정이 진행되고 있습니다"
    
    intro = f"**{name}({ticker})**의 AI 분석 결과, 현재 **{sector} 섹터 내 {tier_desc}**에 위치하며 {trend_desc}."
    report.append(intro)
    
    # Phase 2: Fundamental Context (The "Why")
    # Focus on the strongest point naturally
    sorted_traits = sorted([('성장성', s_growth), ('밸류에이션', s_value), ('재무안정성', s_stability)], key=lambda x: x[1], reverse=True)
    best_trait = sorted_traits[0]
    worst_trait = sorted_traits[-1]
    
    trait_msg = ""
    if best_trait[1] >= 80:
        trait_msg = f"특히 **{best_trait[0]}({best_trait[1]}점)** 부문에서 **매우 우수한 평가**를 받아,"
        if best_trait[0] == '성장성':
            trait_msg += " 미래 실적 기대감이 주가에 반영되고 있습니다."
        elif best_trait[0] == '밸류에이션':
            trait_msg += " 현재 주가는 **저평가 매력**이 높은 구간입니다."
        else:
            trait_msg += " 불확실한 시장에서도 안정적인 방어력을 기대할 수 있습니다."
    elif best_trait[1] >= 60:
        trait_msg = f"펀더멘털 측면에서는 **{best_trait[0]}** 지표가 양호하며 전반적으로 균형 잡힌 모습을 보입니다."
    else:
        trait_msg = "다만 전반적인 펀더멘털 모멘텀은 다소 약한 구간을 지나고 있습니다."
        
    report.append(trait_msg)
    
    # Phase 3: Market Pulse (Consensus + Technicals)
    market_msg = ""
    if upside > 10:
        market_msg = f"월가 역시 **긍정적**입니다. 목표 주가는 현재보다 **{upside:.1f}% 높은 수준**이며,"
    elif upside > -5:
        market_msg = f"월가 컨센서스는 현재 주가를 **적정 수준**으로 평가하고 있으며,"
    else:
        market_msg = f"월가는 현재 주가가 단기적으로 **고평가**되었다고 판단하고 있으나,"
        
    # RSI & MACD Logic (Context-Aware)
    has_macd_gc = 'MACD_GoldenCross' in stock.get('signals', [])
    
    if rsi < 30:
        if has_macd_gc:
            market_msg += f" 기술적으로는 **과매도(RSI {rsi:.1f})** 상태이나, **MACD 골든크로스**가 발생하여 **강력한 반등**이 기대됩니다."
        else:
            market_msg += f" 기술적으로는 **과매도(RSI {rsi:.1f})** 상태라 **반등 가능성**이 높습니다."
    elif rsi > 70:
        if has_macd_gc:
            market_msg += f" 기술적으로 **과열(RSI {rsi:.1f})** 신호가 있으나, **MACD 골든크로스**가 발생하여 **상승 추세가 지속**될 가능성도 있습니다."
        else:
            market_msg += f" 기술적으로 **과열(RSI {rsi:.1f})** 신호가 있어 단기적인 숨고르기가 필요할 수 있습니다."
    else:
        if has_macd_gc:
            market_msg += f" 기술적 지표는 안정적이며, 특히 **MACD 골든크로스**가 발생하여 **상승 모멘텀**이 강화되고 있습니다."
        else:
            market_msg += f" 기술적 지표들도 특이사항 없이 안정적입니다."
            
    report.append(market_msg)
    
    # Phase 4: Conclusion (Verdict)
    # Simple, clean verdict
    conclusion = ""
    if score >= 75:
        conclusion = "종합적으로 **투자를 적극 고려해볼 만한 시점**입니다."
    elif score >= 50:
        conclusion = "종합적으로 **지켜볼 만한 종목**이나, 분할 매수로 접근하는 것이 좋습니다."
    else:
        conclusion = "종합적으로 신규 진입보다는 **관망하며 리스크를 관리**하는 것이 좋습니다."
        
    report.append(conclusion)
    
    return " ".join(report)

# Select samples
samples = []
# 1. Top Rank
samples.extend([d for d in data if d.get('rank', 999) <= 3])
# 2. Some popular ones
popular_tickers = ['NVDA', 'TSLA', 'AAPL', 'AMD', 'PLTR', 'SOXL', 'TQQQ'] # Note: ETFs might not be in data.json or might lack some fields
for t in popular_tickers:
    found = next((d for d in data if d['ticker'] == t), None)
    if found and found not in samples:
        samples.append(found)

# 3. Low Tier/Score
low_score = [d for d in data if d.get('final_score', 0) < 40][:2]
samples.extend(low_score)

# Deduplicate
unique_samples = {s['ticker']: s for s in samples}.values()

print("=== AI Report Samples (Simulation) ===\n")
for s in list(unique_samples)[:10]:
    print(f"📌 {s['ticker']} (Score: {s.get('final_score')})")
    print(f"📝 {generate_report(s)}")
    print("-" * 50 + "\n")
