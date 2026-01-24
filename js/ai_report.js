/**
 * AI Investment Report Generator
 * Generates a natural language analysis based on stock scoring metrics.
 * 
 * @param {Object} stock - Stock data object from data.json
 * @returns {string} HTML string of the generated report
 */
function generateAIReport(stock) {
    if (!stock || !stock.final_score) {
        return "데이터가 부족하여 AI 분석을 생성할 수 없습니다.";
    }

    const name = stock.name || stock.ticker;
    const ticker = stock.ticker;
    const tier = stock.tier || 3;
    const sector = stock.sector || '기타';

    // Unpack Stats
    const stats_bar = stock.stats_bar || {};
    const s_growth = stats_bar.fundamentals || 50; // Proxy for Growth
    const s_value = stats_bar.value || 50;
    const s_stability = stats_bar.stability || 50;
    const s_momentum = stats_bar.momentum || 50;

    const score = stock.final_score;

    // Consensus Data
    const consensus = stock.consensus || {};
    const target_price = consensus.target_price || {};
    let upside = null;
    if (target_price.mean && stock.current_price) {
        upside = ((target_price.mean - stock.current_price) / stock.current_price) * 100;
    }

    // Technical Data
    const rsi = (stock.technical_analysis && stock.technical_analysis.rsi) ? stock.technical_analysis.rsi.value : 50;
    const signals = stock.signals || [];
    const has_macd_gc = signals.includes('MACD_GoldenCross');

    const report = [];

    // --- Phase 1. Intro (Identity & Trend) ---
    let tier_desc = "";
    if (tier === 1) tier_desc = "최상위권(1티어)";
    else if (tier <= 2) tier_desc = "상위권";
    else if (tier <= 3) tier_desc = "중위권";
    else tier_desc = "하위권";

    let trend_desc = "";
    if (s_momentum > 80) trend_desc = "강한 상승세를 타고 있습니다";
    else if (s_momentum > 50) trend_desc = "안정적인 흐름을 유지하고 있습니다";
    else trend_desc = "조정이 진행되고 있습니다"; // Bearish but soft tone

    // intro: "Based on AI analysis..."
    report.push(`<strong>${name}(${ticker})</strong>의 AI 분석 결과, 현재 <strong>${sector} 섹터 내 ${tier_desc}</strong>에 위치하며 ${trend_desc}.`);


    // --- Phase 2. Fundamentals (The Why) ---
    const traits = [
        { name: '성장성', score: s_growth, key: 'growth' },
        { name: '밸류에이션', score: s_value, key: 'value' },
        { name: '재무안정성', score: s_stability, key: 'stability' }
    ];
    // Sort descending by score
    traits.sort((a, b) => b.score - a.score);
    const best = traits[0];

    let fund_msg = "";
    if (best.score >= 80) {
        fund_msg = `특히 <strong>${best.name}(${best.score}점)</strong> 부문에서 <strong>매우 우수한 평가</strong>를 받아,`;
        if (best.key === 'growth') fund_msg += " 미래 실적 기대감이 주가에 반영되고 있습니다.";
        else if (best.key === 'value') fund_msg += " 현재 주가는 <strong>저평가 매력</strong>이 높은 구간입니다.";
        else fund_msg += " 불확실한 시장에서도 안정적인 방어력을 기대할 수 있습니다.";
    } else if (best.score >= 60) {
        fund_msg = `펀더멘털 측면에서는 <strong>${best.name}</strong> 지표가 양호하며 전반적으로 균형 잡힌 모습을 보입니다.`;
    } else {
        fund_msg = "다만 전반적인 펀더멘털 모멘텀은 다소 약한 구간을 지나고 있습니다.";
    }
    report.push(fund_msg);


    // --- Phase 3. Market Pulse (Consensus + Technicals) ---
    let market_msg = "";

    // Consensus
    if (upside !== null) {
        if (upside > 10) {
            market_msg = `월가 역시 <strong>긍정적</strong>입니다. 목표 주가는 현재보다 <strong>${upside.toFixed(1)}% 높은 수준</strong>이며,`;
        } else if (upside > -5) {
            market_msg = `월가 컨센서스는 현재 주가를 <strong>적정 수준</strong>으로 평가하고 있으며,`;
        } else {
            market_msg = `월가는 현재 주가가 단기적으로 <strong>고평가</strong>되었다고 판단하고 있으나,`;
        }
    } else {
        market_msg = "시장 전문가들의 컨센서스 데이터는 부족하지만,";
    }

    // Technicals (RSI & MACD)
    let tech_msg = "";
    if (rsi < 30) {
        // Oversold
        if (has_macd_gc) tech_msg = ` 기술적으로는 <strong>과매도(RSI ${rsi.toFixed(1)})</strong> 상태이며, <strong>MACD 골든크로스</strong>까지 발생하여 <strong>강력한 반등</strong>이 기대됩니다.`;
        else tech_msg = ` 기술적으로는 <strong>과매도(RSI ${rsi.toFixed(1)})</strong> 상태라 <strong>반등 가능성</strong>이 높습니다.`;
    } else if (rsi > 70) {
        // Overbought
        if (has_macd_gc) tech_msg = ` 기술적으로 <strong>과열(RSI ${rsi.toFixed(1)})</strong> 신호가 있으나, <strong>MACD 골든크로스</strong>가 발생하여 <strong>추세가 지속</strong>될 가능성도 열려 있습니다.`;
        else tech_msg = ` 기술적으로 <strong>과열(RSI ${rsi.toFixed(1)})</strong> 신호가 있어 단기적인 숨고르기가 필요할 수 있습니다.`;
    } else {
        // Neutral
        if (has_macd_gc) tech_msg = ` 기술적 지표는 안정적이며, 특히 <strong>MACD 골든크로스</strong>가 발생하여 <strong>상승 모멘텀</strong>이 강화되고 있습니다.`;
        else tech_msg = ` 기술적 지표들도 특이사항 없이 안정적입니다.`;
    }

    report.push(market_msg + tech_msg);


    // --- Phase 4. Conclusion ---
    let conclusion = "";
    if (score >= 75) {
        conclusion = "종합적으로 <strong>투자를 적극 고려해볼 만한 시점</strong>입니다.";
    } else if (score >= 50) {
        conclusion = "종합적으로 <strong>지켜볼 만한 종목</strong>이나, 분할 매수로 접근하는 것이 좋습니다.";
    } else {
        conclusion = "종합적으로 신규 진입보다는 <strong>관망하며 리스크를 관리</strong>하는 것이 좋습니다.";
    }
    report.push(conclusion);

    return report.join(" ");
}

// Expose to window
window.generateAIReport = generateAIReport;
