// --- Safe Rendering Helper ---
function safeRender(fn, data, name = "Section") {
    try {
        return fn(data);
    } catch (e) {
        console.error(`Error rendering ${name}:`, e);
        return `
                    <div class="p-4 bg-red-900/20 border border-red-500/50 rounded-lg text-center my-4">
                        <div class="text-red-400 font-bold text-sm mb-1">⚠️ ${name} 로드 실패</div>
                        <div class="text-gray-500 text-xs">${e.message}</div>
                    </div>
                `;
    }
}

// --- Component Functions ---

function renderTopSection(data) {
    const SECTOR_SLUGS = {
        "기술": "technology", "커뮤니케이션": "communication", "임의소비재": "consumer-discretionary",
        "필수소비재": "consumer-staples", "에너지": "energy", "금융": "financials", "헬스케어": "healthcare",
        "산업재": "industrials", "소재": "materials", "부동산": "real-estate", "유틸리티": "utilities"
    };

    const formatMarketCap = (num) => {
        if (!num) return '-';
        if (num >= 1e12) return (num / 1e12).toFixed(2) + 'T';
        if (num >= 1e9) return (num / 1e9).toFixed(1) + 'B';
        if (num >= 1e6) return (num / 1e6).toFixed(0) + 'M';
        return num.toLocaleString();
    };

    const isPlus = data.change_pct >= 0;
    const changeColor = isPlus ? 'text-red-400' : 'text-blue-400';
    const changeSign = isPlus ? '▲' : '▼';

    let tierClass = 'text-gray-400 border-gray-600 bg-gray-700/20';
    if (data.tier === 1) tierClass = 'text-[#0093ff] border-[#0093ff] bg-[#0093ff]/10';
    else if (data.tier === 2) tierClass = 'text-[#00bba3] border-[#00bba3] bg-[#00bba3]/10';
    else if (data.tier === 3) tierClass = 'text-[#ffb900] border-[#ffb900] bg-[#ffb900]/10';
    else if (data.tier === 4) tierClass = 'text-[#9aa4af] border-[#9aa4af] bg-[#9aa4af]/10';
    else if (data.tier === 5) tierClass = 'text-[#a07557] border-[#a07557] bg-[#a07557]/10';

    const tierBadge = `<span class="px-2 py-0.5 text-sm font-bold rounded border ${tierClass}">${data.tier} TIER</span>`;

    return `
                <nav class="text-xs text-gray-500 mb-3 flex items-center gap-1" aria-label="Breadcrumb">
                    <a href="/" class="hover:text-gray-300 transition">홈</a>
                    <span class="text-gray-600">›</span>
                    <a href="/sector/${SECTOR_SLUGS[data.sector] || '#'}" class="hover:text-gray-300 transition">${data.sector || '기타'}</a>
                    <span class="text-gray-600">›</span>
                    <span class="text-gray-400">${data.ticker}</span>
                </nav>

                <section class="flex flex-row justify-between items-start md:items-end mb-6 gap-4">
                    <div class="flex items-center gap-4 flex-1">
                        <img src="https://financialmodelingprep.com/image-stock/${data.ticker.replace('.', '-')}.png" 
                             alt="${data.name}(${data.ticker}) 주식 로고"
                             loading="lazy"
                             onerror="this.src='https://ui-avatars.com/api/?name=${data.ticker}&background=5383e8&color=fff&size=256'" 
                             style="filter: invert(1) hue-rotate(180deg);" class="w-16 h-16 rounded-lg shadow-lg object-contain">
                        <div class="w-full">
                            <div class="flex items-center gap-2 mb-0.5">
                                <h1 class="text-2xl md:text-3xl font-bold text-white tracking-tight break-keep mr-1">${data.name}</h1>
                                <div id="favoriteContainer" class="cursor-pointer pt-1 shrink-0"></div>
                            </div>
                            
                            <div class="flex justify-between items-start w-full gap-4">
                                <div>
                                    <div class="flex items-center gap-2">
                                        <span class="text-lg font-bold text-gray-400 tracking-wider">${data.ticker}</span>
                                        ${tierBadge}
                                    </div>
                                    <a href="/sector/${SECTOR_SLUGS[data.sector] || '#'}" class="inline-block px-2 py-1 bg-gray-600 text-gray-200 rounded text-xs font-bold hover:bg-gray-500 transition-colors mt-1 hover:text-white hover:no-underline">${data.sector}</a>
                                </div>

                                <div class="text-right md:hidden">
                                    <div class="text-2xl font-bold font-mono">$${data.current_price}</div>
                                    <div class="${changeColor} font-bold text-sm flex items-center justify-end gap-1">
                                        ${data.change_pct > 0 ? '▲' : '▼'} ${data.change_pct}%
                                    </div>
                                    <div class="text-[10px] text-gray-400 font-bold mt-0.5 tracking-wider">
                                        ${formatMarketCap(data.market_cap)}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="text-right hidden md:block">
                        <div class="text-4xl font-bold font-mono">$${data.current_price}</div>
                        <div class="${changeColor} font-bold text-lg flex items-center justify-end gap-1">
                            ${data.change_pct > 0 ? '▲' : '▼'} ${data.change_pct}% <span class="text-xs text-gray-500 font-normal">Today</span>
                        </div>
                        <div class="text-[11px] text-gray-500 font-bold mt-1 tracking-wider">
                           ${formatMarketCap(data.market_cap)}
                        </div>
                    </div>
                </section>
            `;
}

function renderFlipCard(data) {
    return `
                <div class="flip-card-container">
                    <div class="segmented-control">
                        <div id="segmentSlider" class="segment-slider"></div>
                        <button id="tabChart" onclick="toggleFlipCard(false)" class="flip-tab active">📊 차트 보기</button>
                        <button id="tabAnalysis" onclick="toggleFlipCard(true)" class="flip-tab">💰 내 평단 분석</button>
                    </div>
                    <div id="flipCard" class="flip-card rounded-b-xl h-[500px]">
                        <div class="flip-card-front">
                            <div id="tv_chart_container" class="bg-[#131722] rounded-b-xl border border-gray-800 border-t-0 h-[500px] relative overflow-hidden group"></div>
                        </div>
                        <div class="flip-card-back bg-[#131722] rounded-b-xl border border-[#2962ff]/30 border-t-0 h-[500px] p-6 flex flex-col">
                            <div class="text-center mb-6">
                                <h3 class="text-xl font-bold text-white mb-2">💰 내 평단가 분석</h3>
                                <p class="text-gray-400 text-sm">평균 매수가를 입력하면 현재가 대비 손익을 분석해드립니다</p>
                            </div>
                            <div class="flex-1 flex flex-col items-center justify-center gap-6">
                                <div class="w-full max-w-sm space-y-4">
                                    <div>
                                        <label class="block text-gray-400 text-sm mb-2">평균 매수가 ($)</label>
                                        <input type="number" id="avgPriceInput" placeholder="예: 150.00" 
                                            class="w-full bg-[#1e1e28] border border-gray-700 rounded-lg px-4 py-3 text-white text-lg font-mono focus:border-[#2962ff] focus:outline-none focus:ring-2 focus:ring-[#2962ff]/20 transition-all">
                                    </div>
                                    <div>
                                        <label class="block text-gray-400 text-sm mb-2">보유 수량 (주)</label>
                                        <input type="number" id="quantityInput" placeholder="예: 10" 
                                            class="w-full bg-[#1e1e28] border border-gray-700 rounded-lg px-4 py-3 text-white text-lg font-mono focus:border-[#2962ff] focus:outline-none focus:ring-2 focus:ring-[#2962ff]/20 transition-all">
                                    </div>
                                </div>
                                <button id="analyzeBtn" onclick="analyzeAvgPrice()" 
                                    class="bg-gradient-to-r from-[#2962ff] to-[#1e4bd8] text-white font-bold py-3 px-8 rounded-lg hover:shadow-[0_0_25px_rgba(41,98,255,0.5)] transition-all duration-300 hover:scale-105">
                                    🔍 분석하기
                                </button>
                            </div>
                            <div id="analysisResult" class="hidden mt-4 p-4 bg-[#1e1e28] rounded-lg border border-gray-700"></div>
                        </div>
                    </div>
                </div>
            `;
}

function renderConsensus(data) {
    const cons = data.consensus;
    if (!cons || !cons.target_price) return '<div class="text-xs text-gray-500">데이터 없음</div>';

    const current = data.current_price;
    const target = cons.target_price.mean;
    const low = cons.target_price.low;
    const high = cons.target_price.high;
    const score = cons.recommendation ? cons.recommendation.score : 0;
    const status = cons.recommendation ? cons.recommendation.status : 'N/A';

    const upside = ((target - current) / current * 100).toFixed(1);
    const isUpsidePositive = upside >= 0;
    const upsideColor = isUpsidePositive ? 'text-green-400' : 'text-red-400';
    const upsideSign = isUpsidePositive ? '+' : '';

    const valMin = Math.min(low, current, target) * 0.95;
    const valMax = Math.max(high, current, target) * 1.05;
    const fullRange = valMax - valMin;
    const getPos = (val) => ((val - valMin) / fullRange * 100);

    return `
                <div class="text-sm font-bold text-gray-200 mb-4 border-b border-gray-700 pb-2 flex items-center gap-2">
                    <svg class="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    월스트리트 시장 예상치
                </div>
                <div class="flex justify-between items-end mb-6">
                    <div>
                        <div class="text-2xl font-bold text-white flex items-center gap-2">
                            ${status}
                            <span class="text-xs bg-blue-600 text-white px-2 py-0.5 rounded">${score} / 5.0</span>
                        </div>
                    </div>
                    <div class="text-right">
                        <div class="text-gray-400 text-xs">상승 여력</div>
                        <div class="text-xl font-bold ${upsideColor}">${upsideSign}${upside}%</div>
                    </div>
                </div>

                <div class="relative w-full h-20 mt-6 select-none">
                     <div class="absolute top-6 h-2 bg-gradient-to-r from-gray-700 via-gray-600 to-gray-700 rounded-full w-full"></div>
                     <div class="absolute top-4 flex flex-col items-center z-10" style="left: ${getPos(low)}%; transform: translateX(-50%);">
                         <div class="h-6 w-0.5 bg-gray-500 opacity-80"></div>
                         <div class="mt-1 text-[10px] text-gray-500 font-bold">$${low.toFixed(2)}</div>
                         <div class="text-[9px] text-gray-600">Low</div>
                     </div>
                     <div class="absolute top-4 flex flex-col items-center z-10" style="left: ${getPos(high)}%; transform: translateX(-50%);">
                         <div class="h-6 w-0.5 bg-gray-500 opacity-80"></div>
                         <div class="mt-1 text-[10px] text-gray-500 font-bold">$${high.toFixed(2)}</div>
                         <div class="text-[9px] text-gray-600">High</div>
                     </div>
                     <div class="absolute top-4 flex flex-col items-center group cursor-pointer z-10 transition-all duration-1000" style="left: ${getPos(target)}%; transform: translateX(-50%);">
                         <div class="h-6 w-0.5 bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.8)]"></div>
                         <div class="mt-1 text-[10px] text-green-400 font-bold">$${target.toFixed(2)}</div>
                         <div class="text-[9px] text-gray-400">Target</div>
                     </div>
                     <div class="absolute -top-4 flex flex-col items-center z-20 transition-all duration-1000" style="left: ${getPos(current)}%; transform: translateX(-50%);">
                         <div class="mb-1 px-2 py-0.5 bg-gray-600 rounded text-xs text-white font-bold border border-gray-500 shadow-lg whitespace-nowrap">Now $${current}</div>
                         <div class="w-0 h-0 border-l-[6px] border-l-transparent border-r-[6px] border-r-transparent border-t-[8px] border-t-white drop-shadow-md"></div>
                     </div>
                </div>
            `;
}

function renderFinancialHealth(data) {
    const fh = data.financial_health;
    if (!fh) return '<div class="text-center text-gray-500 text-sm py-4">재무 데이터가 없습니다.</div>';

    const thresholds = {
        per: { good: 15, warn: 25, goodLabel: '저평가', badLabel: '고평가', higherBetter: false, tip: '10배 미만이면 저평가' },
        pbr: { good: 1.5, warn: 3, goodLabel: '자산가치↑', badLabel: '고평가', higherBetter: false, tip: '1배 미만 저평가' },
        revenue_growth: { good: 15, warn: 0, goodLabel: '고성장', badLabel: '역성장', higherBetter: true, tip: '매출 증가율' },
        eps_growth: { good: 20, warn: 0, goodLabel: '급성장', badLabel: '감소', higherBetter: true, tip: '이익 증가율' },
        roe: { good: 15, warn: 8, goodLabel: '고수익', badLabel: '저효율', higherBetter: true, tip: '자기자본 이익률' },
        operating_margin: { good: 15, warn: 5, goodLabel: '마진우수', badLabel: '저마진', higherBetter: true, tip: '영업이익률' },
        debt_ratio: { good: 100, warn: 200, goodLabel: '안정', badLabel: '위험', higherBetter: false, tip: '부채 비율' },
        current_ratio: { good: 1.5, warn: 1, goodLabel: '유동성↑', badLabel: '주의', higherBetter: true, tip: '단기 지급능력' }
    };

    const evaluate = (val, t) => {
        if (val === null || val === undefined) return { color: 'text-gray-500', badge: null };
        const good = t.higherBetter ? val >= t.good : val <= t.good;
        const warn = t.higherBetter ? val >= t.warn : val <= t.warn;
        if (good) return { color: 'text-green-400', badge: t.goodLabel, badgeColor: 'bg-green-500/20 text-green-400' };
        if (warn) return { color: 'text-gray-300', badge: null };
        return { color: 'text-red-400', badge: t.badLabel, badgeColor: 'bg-red-500/20 text-red-400' };
    };

    const format = (key, val, suffix = '') => {
        if (val === null || val === undefined) return '<span class="text-gray-500">-</span>';
        const status = evaluate(val, thresholds[key]);
        const badge = status.badge ? `<span class="ml-1 text-[9px] px-1.5 py-0.5 rounded ${status.badgeColor}">${status.badge}</span>` : '';
        return `<span class="${status.color} font-bold">${val}${suffix}</span>${badge}`;
    };

    const tooltip = (key) => `<span class="text-gray-500 text-[10px] ml-1 cursor-help" title="${thresholds[key].tip}">ⓘ</span>`;

    return `
                 <div class="bg-[#1e1e24] rounded-lg p-4 border border-gray-700 mb-3">
                     <span class="text-sm font-bold text-gray-200 mb-2 block">가치 평가</span>
                     <div class="grid grid-cols-2 gap-4">
                         <div><div class="text-xs text-gray-400 flex items-center">PER${tooltip('per')}</div><div class="text-lg">${format('per', fh.per, '배')}</div></div>
                         <div><div class="text-xs text-gray-400 flex items-center">PBR${tooltip('pbr')}</div><div class="text-lg">${format('pbr', fh.pbr, '배')}</div></div>
                     </div>
                 </div>
                 <div class="bg-[#1e1e24] rounded-lg p-4 border border-gray-700 mb-3">
                     <span class="text-sm font-bold text-gray-200 mb-2 block">성장성</span>
                     <div class="grid grid-cols-2 gap-4">
                         <div><div class="text-xs text-gray-400 flex items-center">매출성장${tooltip('revenue_growth')}</div><div class="text-lg">${format('revenue_growth', fh.revenue_growth, '%')}</div></div>
                         <div><div class="text-xs text-gray-400 flex items-center">EPS성장${tooltip('eps_growth')}</div><div class="text-lg">${format('eps_growth', fh.eps_growth, '%')}</div></div>
                     </div>
                 </div>
                 <div class="bg-[#1e1e24] rounded-lg p-4 border border-gray-700">
                     <div class="grid grid-cols-2 gap-4">
                         <div><div class="text-xs text-gray-400 flex items-center">ROE${tooltip('roe')}</div><div class="text-lg">${format('roe', fh.roe, '%')}</div></div>
                         <div><div class="text-xs text-gray-400 flex items-center">부채비율${tooltip('debt_ratio')}</div><div class="text-lg">${format('debt_ratio', fh.debt_ratio, '%')}</div></div>
                     </div>
                 </div>
            `;
}

function renderNaspickScore(data) {
    const stats = data.stats_bar || { fundamentals: 0, value: 0, momentum: 0, stability: 0, risk: 0, consensus: 0 };
    const bars = [
        { k: 'Fundamentals', label: '📈 Fundamentals (실적/성장)', c: 'blue' },
        { k: 'Value', label: '💰 Value (가치평가)', c: 'amber' },
        { k: 'Momentum', label: '🚀 Momentum (상승탄력)', c: 'rose' },
        { k: 'Stability', label: '🛡️ Stability (재무안정)', c: 'cyan' },
        { k: 'Risk', label: '⚡ Risk (저변동성)', c: 'purple' },
        { k: 'Consensus', label: '🌐 Consensus (월가전망)', c: 'green' }
    ];

    return `
                 <h2 class="text-sm font-bold text-gray-200 mb-4 border-b border-gray-700 pb-2 flex items-center gap-2">
                     <svg class="w-4 h-4 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"></path></svg>
                     나스픽 점수 분석
                 </h2>
                 <div class="flex items-end gap-2 mb-6">
                     <span class="text-5xl font-extrabold text-[#5383e8] tracking-tighter">${data.final_score}</span>
                     <span class="text-lg font-bold text-gray-500 mb-2">/ 100</span>
                 </div>
                 <div class="space-y-4">
                     ${bars.map(item => {
        const val = stats[item.k.toLowerCase()] || 0;
        // Tailwind colors need to be safelisted or full strings, but here we construct class strings
        // assuming standard palette is available
        const textColor = `text-${item.c}-400`;
        const barColor = `from-${item.c}-600 to-${item.c}-400`;
        const shadow = `shadow-${item.c}-500/50`; // approximation for shadow color
        return `
                             <div>
                                 <div class="flex justify-between text-xs mb-1.5">
                                     <span class="text-gray-300 font-bold">${item.label}</span>
                                     <span class="${textColor} font-bold">${val}%</span>
                                 </div>
                                 <div class="w-full bg-gray-700 h-2 rounded-full overflow-hidden">
                                     <div class="bg-gradient-to-r ${barColor} h-full shadow-[0_0_10px_rgba(0,0,0,0.3)]" style="width: ${val}%"></div>
                                 </div>
                             </div>
                         `;
    }).join('')}
                 </div>
            `;
}

// [RESTORED] Full Technical Analysis Logic
function renderTechnical(data) {
    const ta = data.technical_analysis || {};
    let html = `<h3 class="flex items-center gap-2 text-sm font-bold text-gray-200 mb-4 border-b border-gray-700 pb-2">
                <svg class="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
                기술적 분석
             </h3><div class="space-y-4">`;

    // 1. Candle Pattern
    const cp = ta.candle_pattern;
    if (cp) {
        const imgPath = '/images/candle_patterns/' + cp.pattern + '.png';
        html += `
                    <div class="bg-[#1e1e24] rounded-lg p-3 border border-gray-700">
                        <div class="text-[10px] text-gray-500 uppercase tracking-wider mb-2">캔들 패턴</div>
                        <div class="flex items-center gap-3">
                            <img src="${imgPath}" alt="${cp.name_kr}" class="w-12 h-12 object-contain" onerror="this.style.display='none'">
                            <div>
                                <div class="text-sm font-bold ${cp.signal === 'bullish' ? 'text-green-400' : 'text-red-400'}">${cp.name_kr}</div>
                                <div class="text-[10px] text-gray-500">${cp.desc} (${cp.date})</div>
                            </div>
                        </div>
                    </div>
                `;
    } else {
        html += `
                    <div class="bg-[#1e1e24] rounded-lg p-3 border border-gray-700">
                        <div class="text-[10px] text-gray-500 uppercase tracking-wider mb-1">캔들 패턴</div>
                        <div class="text-xs text-gray-500">최근 5일 내 특이 패턴 없음</div>
                    </div>
                `;
    }

    // 2. RSI (Restored Full Gauge)
    const rsi = ta.rsi || { value: 50, status: 'neutral' };
    const rsiColor = rsi.status === 'overbought' ? 'text-red-400' : rsi.status === 'oversold' ? 'text-blue-400' : 'text-gray-400';
    const rsiLabel = rsi.status === 'overbought' ? '과매수' : rsi.status === 'oversold' ? '과매도' : '중립';

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
                    <div class="text-center mt-2"><span class="text-2xl font-bold ${rsiColor}">${rsi.value}</span></div>
                </div>
             `;

    // 3. Volume
    const vol = ta.volume || { pct_change: 0 };
    const volColor = vol.pct_change >= 0 ? 'text-red-400' : 'text-blue-400';
    const volSign = vol.pct_change >= 0 ? '+' : '';
    html += `
                <div class="bg-[#1e1e24] rounded-lg p-3 border border-gray-700">
                    <div class="text-[10px] text-gray-500 uppercase tracking-wider mb-2">거래량 <span class="normal-case">(전일)</span></div>
                    <div class="flex items-center gap-2">
                        <div class="${volColor} text-sm font-bold">평균 대비 ${volSign}${vol.pct_change}%</div>
                    </div>
                </div>
             `;

    html += '</div>';
    return html;
}

// [RESTORED] Full Calendar Logic
function renderCalendar(data) {
    const cal = data.calendar || {};

    // Earnings Logic
    let earningsHtml = '';
    let nextHtml = '';
    if (cal.next_earnings) {
        const todayMs = new Date().setHours(0, 0, 0, 0);
        const nextDate = new Date(cal.next_earnings);
        const diffDays = Math.ceil((nextDate.setHours(0, 0, 0, 0) - todayMs) / (1000 * 60 * 60 * 24));

        let dDay = '';
        let alertIcon = '';
        if (diffDays >= 0) {
            if (diffDays <= 7) { dDay = `<span class="text-orange-400 font-bold ml-2">D-${diffDays}</span>`; alertIcon = '🔔'; }
            else if (diffDays <= 14) { dDay = `<span class="text-gray-400 ml-2">D-${diffDays}</span>`; }

            nextHtml = `<div class="text-xs text-gray-400 mb-1 flex items-center">다음 실적 발표 ${dDay}</div>
                                 <div class="text-sm font-bold text-gray-200 flex items-center gap-2">${cal.next_earnings} ${alertIcon}</div>`;
        } else {
            nextHtml = `<div class="text-xs text-gray-400 mb-1 flex items-center">직전 실적 발표 <span class="text-gray-600 ml-2 text-[10px]">(종료)</span></div>
                                 <div class="text-sm font-bold text-gray-500 flex items-center gap-2">${cal.next_earnings}</div>`;
        }
    } else {
        nextHtml = `<div class="text-xs text-gray-400 mb-1">실적 발표</div><div class="text-sm text-gray-500">일정 미정</div>`;
    }

    // Past Earnings Surprise
    let pastHtml = '';
    if (cal.last_earnings_date && cal.last_surprise !== undefined) {
        const isBeat = cal.last_surprise > 0;
        const color = isBeat ? 'text-green-400' : 'text-red-400';
        const label = isBeat ? '어닝 서프라이즈' : '어닝 쇼크';
        pastHtml = `
                    <div class="mt-3 pt-3 border-t border-gray-700/50">
                        <div class="text-xs text-gray-400 mb-1 flex justify-between">
                            <span>직전 실적 (${cal.last_earnings_date})</span>
                            <span class="${color} font-bold text-[10px] bg-gray-700/50 px-1.5 rounded">${label}</span>
                        </div>
                        <div class="flex justify-between items-end">
                            <div class="text-[10px] text-gray-500">예상 ${cal.last_eps_est || '-'} / 실제 <span class="text-gray-200 font-bold">${cal.last_eps_act || '-'}</span></div>
                            <div class="${color} font-bold text-sm">${isBeat ? '+' : ''}${Number(cal.last_surprise).toFixed(2)}%</div>
                        </div>
                    </div>
                 `;
    }
    earningsHtml = nextHtml + pastHtml;

    // Dividend Logic
    let divHtml = '';
    const exDate = cal.ex_dividend_date;
    const amount = cal.dividend_amount ? `$${cal.dividend_amount.toFixed(2)}` : '-';

    if (!exDate || exDate === '-') {
        divHtml = '<div><div class="text-xs text-gray-400 mb-2">배당</div><div class="text-xs text-gray-500 text-center py-2">배당 정보 없음</div></div>';
    } else {
        const todayMs = new Date().setHours(0, 0, 0, 0);
        const exMs = new Date(exDate).setHours(0, 0, 0, 0);
        const isFuture = exMs >= todayMs;

        let statusBadge = isFuture ? '<span class="text-blue-400 text-[10px] ml-1 bg-blue-500/10 px-1 rounded border border-blue-500/30">예정</span>'
            : '<span class="text-gray-500 text-[10px] ml-1 bg-gray-700/50 px-1 rounded">지급완료</span>'; // Simplified for safety
        let dateColor = isFuture ? 'text-gray-200' : 'text-gray-500';

        divHtml = `
                    <div>
                        <div class="text-xs text-gray-400 mb-2">배당</div>
                        <div class="space-y-4">
                            <div class="flex justify-between items-start">
                                <div>
                                    <div class="text-[10px] text-gray-500 mb-0.5 flex items-center">${isFuture ? '다음 배당락일' : '최근 배당락일'} ${statusBadge}</div>
                                    <div class="text-sm font-bold ${dateColor}">${exDate}</div>
                                </div>
                                <div class="text-right">
                                    <div class="text-[10px] text-gray-500 mb-0.5">배당금 (1주당)</div>
                                    <div class="text-sm font-bold text-gray-200">${amount}</div>
                                </div>
                            </div>
                            <div class="flex justify-between items-center text-[10px] text-gray-500 bg-gray-800/50 p-2 rounded">
                                <div>지급일: ${cal.dividend_payment_date || '-'}</div>
                                <div>수익률: <span class="text-gray-300 font-bold">${cal.dividend_yield ? cal.dividend_yield + '%' : '-'}</span></div>
                            </div>
                        </div>
                    </div>
                 `;
    }

    return `
                 <div class="bg-[#282830] rounded-xl border border-gray-800 p-5">
                    <h4 class="text-sm font-bold text-gray-200 mb-4 border-b border-gray-700 pb-2 flex items-center gap-2">
                        <svg class="w-4 h-4 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                        투자 캘린더
                    </h4>
                    <div class="space-y-4">
                        <div>${earningsHtml}</div>
                        <div class="w-full h-px bg-gray-700/50 my-2"></div>
                        ${divHtml}
                    </div>
                 </div>
             `;
}

// [RESTORED] Full Related Stocks Logic with Tabs
function renderRelatedStocks(data) {
    const peers = data.related_peers || [];
    const similars = data.similar_score_peers || [];
    // We need full data for name lookups, assume window.allData is available
    const allData = window.allData || [];

    const renderList = (list, emptyMsg) => {
        if (!list.length) return `<div class="text-xs text-gray-600">${emptyMsg}</div>`;
        return list.map(p => {
            const d = allData.find(x => x.ticker === p.ticker) || { name: p.ticker };
            const isPlus = p.change_pct >= 0;
            return `
                        <a href="/stock/${p.ticker}" class="flex justify-between items-center border-b border-gray-800 pb-2 cursor-pointer hover:bg-gray-800 transition p-2 rounded group block text-inherit hover:no-underline">
                            <div class="flex items-center gap-3">
                                <div class="w-10 h-10 rounded flex items-center justify-center p-0.5 shrink-0 overflow-hidden">
                                     <img src="https://financialmodelingprep.com/image-stock/${p.ticker.replace('.', '-')}.png" 
                                          loading="lazy"
                                          onerror="this.src='https://ui-avatars.com/api/?name=${p.ticker}&background=5383e8&color=fff&size=128'" 
                                          style="filter: invert(1) hue-rotate(180deg);" class="w-full h-full object-contain">
                                </div>
                                <div>
                                    <div class="font-bold text-gray-200 text-sm group-hover:text-blue-400 transition">${d.name}</div>
                                    <div class="text-xs text-gray-500 font-medium">${p.ticker}</div>
                                </div>
                            </div>
                            <span class="${isPlus ? 'text-red-400' : 'text-blue-400'} font-mono text-sm font-bold bg-[#1c1c1f] px-2 py-1 rounded">${isPlus ? '+' : ''}${p.change_pct}%</span>
                        </a>
                    `;
        }).join('');
    };

    return `
                 <div class="bg-[#23232a] rounded-xl border border-gray-800 p-5">
                     <div class="flex items-center justify-between mb-4 border-b border-gray-700 pb-3">
                         <h4 class="text-sm font-bold text-gray-200 flex items-center gap-2">
                             <svg class="w-4 h-4 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
                             관련 종목
                         </h4>
                         <div class="flex bg-gray-700/50 rounded-lg p-0.5">
                             <button id="tabSectorLeader" onclick="switchRelatedTab('sector')" class="px-2.5 py-1 text-[10px] font-bold rounded-md transition-all bg-[#5383e8] text-white">섹터 TOP3</button>
                             <button id="tabSimilarScore" onclick="switchRelatedTab('similar')" class="px-2.5 py-1 text-[10px] font-bold rounded-md transition-all text-gray-400 hover:text-gray-200">유사 점수</button>
                         </div>
                     </div>
                     <div id="sectorLeaderList" class="space-y-3">${renderList(peers, '관련 종목 없음')}</div>
                     <div id="similarScoreList" class="space-y-3 hidden">${renderList(similars, '유사 점수 종목 없음')}</div>
                 </div>
            `;
}

function renderPage(data) {
    console.log("Rendering page for:", data.ticker);
    window.currentStockPrice = data.current_price;
    const main = document.getElementById('mainContent');

    // Assemble sections safely
    const topHtml = safeRender(renderTopSection, data, "상단 정보");
    const flipCardHtml = safeRender(renderFlipCard, data, "차트/분석 카드");

    // Grid Layout
    const consensusHtml = safeRender(renderConsensus, data, "월가 전망");
    const financialHtml = safeRender(renderFinancialHealth, data, "재무 건전성");
    const scoreHtml = safeRender(renderNaspickScore, data, "나스픽 점수");
    const technicalHtml = safeRender(renderTechnical, data, "기술적 분석");
    const calendarHtml = safeRender(renderCalendar, data, "캘린더");
    const relatedHtml = safeRender(renderRelatedStocks, data, "관련 종목");

    const html = `
                ${topHtml}
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <div class="lg:col-span-2 flex flex-col gap-6 lg:gap-4">
                        ${flipCardHtml}
                        
                        <!-- Desktop View -->
                        <div class="bg-[#282830] rounded-xl border border-gray-800 p-6 hidden lg:block">
                            ${consensusHtml}
                        </div>
                         <div class="bg-[#282830] rounded-xl border border-gray-800 p-6 hidden lg:block">
                            <h3 class="flex items-center gap-2 text-sm font-bold text-gray-200 mb-4 border-b border-gray-700 pb-2">
                                <svg class="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"></path></svg>
                                재무 건전성 점검
                            </h3>
                            <div class="space-y-3">${financialHtml}</div>
                        </div>

                        <!-- Mobile View -->
                         <div class="bg-[#282830] rounded-xl border border-gray-800 p-6 block lg:hidden">
                            ${consensusHtml}
                        </div>
                         <div class="bg-[#282830] rounded-xl border border-gray-800 p-6 block lg:hidden">
                            <h3 class="flex items-center gap-2 text-sm font-bold text-gray-200 mb-4 border-b border-gray-700 pb-2">재무 건전성 점검</h3>
                            <div class="space-y-3">${financialHtml}</div>
                        </div>
                        
                        <div class="bg-[#282830] rounded-xl border border-gray-800 p-5">
                            ${technicalHtml}
                        </div>
                    </div>

                    <div class="flex flex-col gap-4">
                        <div class="bg-[#282830] rounded-xl border border-gray-700 p-6 relative overflow-hidden shadow-2xl">
                            ${scoreHtml}
                        </div>
                        
                        ${calendarHtml}
                        ${relatedHtml}

                        <!-- FAQ Section Placeholder -->
                        <div id="faqSection"></div> 
                    </div>
                </div>
            `;

    main.innerHTML = html;

    // Post-render actions
    safeRender(renderFAQ, data, "FAQ");
    safeRender(initFavorites, data.ticker, "Favorites");
    if (window.TradingView) {
        try {
            new TradingView.widget({
                "autosize": true,
                "symbol": (data.exchange ? data.exchange + ":" : "") + data.ticker,
                "interval": "D",
                "timezone": "Etc/UTC",
                "theme": "dark",
                "style": "1",
                "locale": "en",
                "enable_publishing": false,
                "allow_symbol_change": true,
                "container_id": "tv_chart_container",
                "studies": ["BB@tv-basicstudies"]
            });
        } catch (e) { console.error("TradingView Error:", e); }
    }
}


// --- Global Event Handlers ---

function toggleFlipCard(showBack) {
    const card = document.getElementById('flipCard');
    const slider = document.getElementById('segmentSlider');
    const tabChart = document.getElementById('tabChart');
    const tabAnalysis = document.getElementById('tabAnalysis');
    
    if (showBack) {
        card.classList.add('flipped');
        slider.style.transform = 'translateX(100%)';
        tabChart.classList.remove('active');
        tabAnalysis.classList.add('active');
    } else {
        card.classList.remove('flipped');
        slider.style.transform = 'translateX(0)';
        tabChart.classList.add('active');
        tabAnalysis.classList.remove('active');
    }
}

function switchRelatedTab(type) {
    const sectorList = document.getElementById('sectorLeaderList');
    const similarList = document.getElementById('similarScoreList');
    const tabSector = document.getElementById('tabSectorLeader');
    const tabSimilar = document.getElementById('tabSimilarScore');

    if (!sectorList || !similarList) return;

    if (type === 'sector') {
        sectorList.classList.remove('hidden');
        similarList.classList.add('hidden');
        
        tabSector.classList.remove('text-gray-400', 'hover:text-gray-200');
        tabSector.classList.add('bg-[#5383e8]', 'text-white');
        
        tabSimilar.classList.remove('bg-[#5383e8]', 'text-white');
        tabSimilar.classList.add('text-gray-400', 'hover:text-gray-200');
    } else {
        sectorList.classList.add('hidden');
        similarList.classList.remove('hidden');
        
        tabSimilar.classList.remove('text-gray-400', 'hover:text-gray-200');
        tabSimilar.classList.add('bg-[#5383e8]', 'text-white');
        
        tabSector.classList.remove('bg-[#5383e8]', 'text-white');
        tabSector.classList.add('text-gray-400', 'hover:text-gray-200');
    }
}

function analyzeAvgPrice() {
    const avgInput = document.getElementById('avgPriceInput');
    const qtyInput = document.getElementById('quantityInput');
    const resultDiv = document.getElementById('analysisResult');
    
    if (!avgInput || !qtyInput || !resultDiv) return;

    const avgPrice = parseFloat(avgInput.value);
    const quantity = parseFloat(qtyInput.value);

    if (!avgPrice || avgPrice <= 0) {
        alert('유효한 매수가를 입력해주세요.'); 
        return;
    }

    // Try global var first, then DOM fallback
    let cp = window.currentStockPrice;
    if (!cp) {
         const priceEl = document.querySelector('.text-4xl'); // Desktop price
         if(priceEl) {
             const txt = priceEl.textContent.replace('$','').replace(',','');
             cp = parseFloat(txt);
         }
    }
    
    if (!cp) {
        resultDiv.innerHTML = '<div class="text-red-400 text-center">현재가 정보를 불러올 수 없습니다.</div>';
        resultDiv.classList.remove('hidden');
        return;
    }

    const pnlPercent = ((cp - avgPrice) / avgPrice * 100).toFixed(2);
    const pnlAmount = quantity ? ((cp - avgPrice) * quantity).toFixed(2) : null;
    const isProfit = pnlPercent >= 0;
    const color = isProfit ? 'text-green-400' : 'text-red-400';
    const sign = isProfit ? '+' : '';

    resultDiv.innerHTML = `
        <div class="text-center">
             <div class="text-gray-400 text-xs mb-1">현재가 $${cp} / 평단가 $${avgPrice}</div>
             <div class="text-3xl font-bold ${color} mb-1">${sign}${pnlPercent}%</div>
             ${pnlAmount ? `<div class="text-lg ${color} font-bold">${sign}$${pnlAmount}</div>` : ''}
        </div>
    `;
    resultDiv.classList.remove('hidden');
}
