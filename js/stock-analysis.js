
// Stock Analysis Rendering Module
// This file handles HTML generation for technical analysis, calendar, and volume profile features.
// It is designed to be included in page.html and en/page.html to avoid template literal nesting issues.

window.renderTechnicalAnalysis = function (ta) {
    if (!ta) return '';

    let html = '';

    // 1. Candle Pattern
    const cp = ta.candle_pattern;
    if (cp) {
        const imgPath = `/images/candle_patterns/${cp.pattern}.png`;
        const signalColor = cp.signal === 'bullish' ? 'text-green-400' : 'text-red-400';
        html += `
        <div class="bg-[#1e1e24] rounded-lg p-3 border border-gray-700">
            <div class="text-[10px] text-gray-500 uppercase tracking-wider mb-2">캔들 패턴</div>
            <div class="flex items-center gap-3">
                <img src="${imgPath}" alt="${cp.name_kr}" class="w-12 h-12 object-contain"
                    onerror="this.style.display='none'">
                <div>
                    <div class="text-sm font-bold ${signalColor}">${cp.name_kr}</div>
                    <div class="text-[10px] text-gray-500">${cp.desc} (${cp.date})</div>
                </div>
            </div>
        </div>`;
    } else {
        html += `
        <div class="bg-[#1e1e24] rounded-lg p-3 border border-gray-700">
            <div class="text-[10px] text-gray-500 uppercase tracking-wider mb-1">캔들 패턴</div>
            <div class="text-xs text-gray-500">최근 5일 내 특이 패턴 없음</div>
        </div>`;
    }

    // 2. RSI (Gauge Chart Style)
    const rsi = ta.rsi || { value: 50, status: 'neutral' };
    const rsiColor = rsi.status === 'overbought' ? 'text-red-400' :
        rsi.status === 'oversold' ? 'text-blue-400' : 'text-gray-400';
    const rsiLabel = rsi.status === 'overbought' ? '과매수' :
        rsi.status === 'oversold' ? '과매도' :
            rsi.status === 'bullish' ? '강세' : '약세';

    html += `
    <div class="bg-[#1e1e24] rounded-lg p-3 border border-gray-700">
        <div class="flex justify-between items-center mb-3">
            <div class="text-[10px] text-gray-500 uppercase tracking-wider">RSI (14)</div>
            <div class="${rsiColor} text-xs font-bold">${rsiLabel}</div>
        </div>
        <div class="relative">
            <div class="h-3 rounded-full overflow-hidden flex">
                <div class="w-[30%] bg-gradient-to-r from-blue-600 to-blue-500"></div>
                <div class="w-[40%] bg-gradient-to-r from-blue-500 via-gray-600 to-red-500"></div>
                <div class="w-[30%] bg-gradient-to-r from-red-500 to-red-600"></div>
            </div>
            <div class="absolute top-0 h-3 flex items-center" style="left: ${rsi.value}%; transform: translateX(-50%);">
                <div class="w-1 h-5 bg-white rounded shadow-lg shadow-white/50"></div>
            </div>
            <div class="flex justify-between text-[8px] text-gray-600 mt-1">
                <span>0</span><span class="text-blue-500">30</span><span class="text-gray-400">50</span><span class="text-red-500">70</span><span>100</span>
            </div>
        </div>
        <div class="text-center mt-2">
            <span class="text-2xl font-bold ${rsiColor}">${rsi.value}</span>
        </div>
    </div>`;

    // 3. Volume
    const vol = ta.volume || { pct_change: 0, status: 'normal' };
    const volColor = vol.pct_change >= 0 ? 'text-red-400' : 'text-blue-400';
    const volSign = vol.pct_change >= 0 ? '+' : '';

    html += `
    <div class="bg-[#1e1e24] rounded-lg p-3 border border-gray-700">
        <div class="text-[10px] text-gray-500 uppercase tracking-wider mb-2">거래량 <span class="normal-case">(전일)</span></div>
        <div class="flex items-center gap-2">
            <div class="${volColor} text-sm font-bold">평균 대비 ${volSign}${vol.pct_change}%</div>
        </div>
    </div>`;

    return html;
};

window.renderCalendar = function (cal, isEn) {
    if (!cal) return '';

    const earningsDate = cal.next_earnings || 'TBD';
    const divAmt = cal.dividend_amount ? `$${cal.dividend_amount.toFixed(2)}` : '-';

    // Earnings Logic
    let earningsDday = '';

    if (earningsDate !== 'TBD') {
        const todayMs = new Date().setHours(0, 0, 0, 0);
        const targetMs = new Date(earningsDate).setHours(0, 0, 0, 0);
        const diffDays = Math.ceil((targetMs - todayMs) / (1000 * 60 * 60 * 24));

        if (diffDays >= 0 && diffDays <= 7) {
            earningsDday = `<span class="text-orange-400 font-bold ml-2">D-${diffDays}</span>`;
        } else if (diffDays > 7 && diffDays <= 14) {
            earningsDday = `<span class="text-gray-400 ml-2">D-${diffDays}</span>`;
        } else if (diffDays < 0) {
            earningsDday = `<span class="text-gray-600 ml-2 text-[10px]">(Passed)</span>`;
        }
    }

    const labels = isEn ? {
        earnings: "Next Earnings",
        dividend: "Dividend",
        exDate: "Ex-Div Date",
        payDate: "Pay Date"
    } : {
        earnings: "실적 발표",
        dividend: "배당금",
        exDate: "배당락일",
        payDate: "지급일"
    };

    return `
    <div class="grid grid-cols-2 gap-3 text-xs">
        <div class="bg-[#1e1e24] p-3 rounded-lg border border-gray-800">
            <div class="text-gray-500 mb-1">${labels.earnings}</div>
            <div class="font-bold text-gray-200 flex items-center">
                ${earningsDate} ${earningsDday}
            </div>
        </div>
        <div class="bg-[#1e1e24] p-3 rounded-lg border border-gray-800">
            <div class="text-gray-500 mb-1">${labels.dividend}</div>
            <div class="font-bold text-gray-200">${divAmt}</div>
        </div>
        <div class="bg-[#1e1e24] p-3 rounded-lg border border-gray-800">
            <div class="text-gray-500 mb-1">${labels.exDate}</div>
            <div class="font-bold text-gray-200">${cal.ex_dividend_date || '-'}</div>
        </div>
        <div class="bg-[#1e1e24] p-3 rounded-lg border border-gray-800">
            <div class="text-gray-500 mb-1">${labels.payDate}</div>
            <div class="font-bold text-gray-200">${cal.dividend_payment_date || '-'}</div>
        </div>
    </div>`;
};
