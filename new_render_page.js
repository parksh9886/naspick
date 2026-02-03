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
    const changeSign = isPlus ? '▲' : '▼'; // Corrected arrow directions for Korean stock market convention (Red=Up)

    let tierClass = 'text-gray-400 border-gray-600 bg-gray-700/20';
    if (data.tier === 1) tierClass = 'text-[#0093ff] border-[#0093ff] bg-[#0093ff]/10';
    else if (data.tier === 2) tierClass = 'text-[#00bba3] border-[#00bba3] bg-[#00bba3]/10';
    else if (data.tier === 3) tierClass = 'text-[#ffb900] border-[#ffb900] bg-[#ffb900]/10';
    else if (data.tier === 4) tierClass = 'text-[#9aa4af] border-[#9aa4af] bg-[#9aa4af]/10';
    else if (data.tier === 5) tierClass = 'text-[#a07557] border-[#a07557] bg-[#a07557]/10';

    const tierBadge = `<span class="px-2 py-0.5 text-sm font-bold rounded border ${tierClass}">${data.tier} TIER</span>`;

    return `
                <!-- Breadcrumb Navigation -->
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

                                <!-- Mobile Price Block -->
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
                    
                    <!-- Desktop Price Block -->
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
                <!-- 3D Flip Card for Chart + Average Price Analysis -->
                <div class="flip-card-container">
                    <!-- Tab Switch Controller -->
                    <div class="segmented-control">
                        <div id="segmentSlider" class="segment-slider"></div>
                        <button id="tabChart" onclick="toggleFlipCard(false)" class="flip-tab active">
                            📊 차트 보기
                        </button>
                        <button id="tabAnalysis" onclick="toggleFlipCard(true)" class="flip-tab">
                            💰 내 평단 분석
                        </button>
                    </div>
                    
                    <!-- Flip Card -->
                    <div id="flipCard" class="flip-card rounded-b-xl h-[500px]">
                        <!-- Front: TradingView Chart -->
                        <div class="flip-card-front">
                            <div id="tv_chart_container" class="bg-[#131722] rounded-b-xl border border-gray-800 border-t-0 h-[500px] relative overflow-hidden group"></div>
                        </div>
                        
                        <!-- Back: Average Price Analysis -->
                        <div class="flip-card-back bg-[#131722] rounded-b-xl border border-[#2962ff]/30 border-t-0 h-[500px] p-6 flex flex-col">
                            <div class="text-center mb-6">
                                <h3 class="text-xl font-bold text-white mb-2">💰 내 평단가 분석</h3>
                                <p class="text-gray-400 text-sm">평균 매수가를 입력하면 현재가 대비 손익을 분석해드립니다</p>
                            </div>
                            
                            <!-- Input Form -->
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
                            
                            <!-- Analysis Result Placeholder -->
                            <div id="analysisResult" class="hidden mt-4 p-4 bg-[#1e1e28] rounded-lg border border-gray-700"></div>
                        </div>
                    </div>
                </div>
            `;
}

function renderConsensus(data) {
    const cons = data.consensus;
    if (!cons || !cons.target_price) {
        return `
                    <div class="flex items-center justify-between mb-4">
                        <div class="text-gray-400 text-xs font-bold uppercase tracking-wider">Wall St. Consensus</div>
                        <div class="text-xs text-gray-500">데이터 없음</div>
                    </div>
                `;
    }

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
                    <svg class="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
                    </svg>
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
                     <!-- Markers -->
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
        per: { good: 15, warn: 25, goodLabel: '저평가', badLabel: '고평가', higherBetter: false },
        pbr: { good: 1.5, warn: 3, goodLabel: '자산가치↑', badLabel: '고평가', higherBetter: false },
        revenue_growth: { good: 15, warn: 0, goodLabel: '고성장', badLabel: '역성장', higherBetter: true },
        eps_growth: { good: 20, warn: 0, goodLabel: '급성장', badLabel: '감소', higherBetter: true },
        roe: { good: 15, warn: 8, goodLabel: '고수익', badLabel: '저효율', higherBetter: true },
        operating_margin: { good: 15, warn: 5, goodLabel: '마진우수', badLabel: '저마진', higherBetter: true },
        debt_ratio: { good: 100, warn: 200, goodLabel: '안정', badLabel: '위험', higherBetter: false },
        current_ratio: { good: 1.5, warn: 1, goodLabel: '유동성↑', badLabel: '주의', higherBetter: true }
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

    return `
                 <!-- 가치 -->
                 <div class="bg-[#1e1e24] rounded-lg p-4 border border-gray-700 mb-3">
                     <span class="text-sm font-bold text-gray-200 mb-2 block">가치 평가</span>
                     <div class="grid grid-cols-2 gap-4">
                         <div><div class="text-xs text-gray-400">PER</div><div class="text-lg">${format('per', fh.per, '배')}</div></div>
                         <div><div class="text-xs text-gray-400">PBR</div><div class="text-lg">${format('pbr', fh.pbr, '배')}</div></div>
                     </div>
                 </div>
                 <!-- 성장 -->
                 <div class="bg-[#1e1e24] rounded-lg p-4 border border-gray-700 mb-3">
                     <span class="text-sm font-bold text-gray-200 mb-2 block">성장성</span>
                     <div class="grid grid-cols-2 gap-4">
                         <div><div class="text-xs text-gray-400">매출성장</div><div class="text-lg">${format('revenue_growth', fh.revenue_growth, '%')}</div></div>
                         <div><div class="text-xs text-gray-400">EPS성장</div><div class="text-lg">${format('eps_growth', fh.eps_growth, '%')}</div></div>
                     </div>
                 </div>
                 <!-- 수익/안정 -->
                 <div class="bg-[#1e1e24] rounded-lg p-4 border border-gray-700">
                     <div class="grid grid-cols-2 gap-4">
                         <div><div class="text-xs text-gray-400">ROE</div><div class="text-lg">${format('roe', fh.roe, '%')}</div></div>
                         <div><div class="text-xs text-gray-400">부채비율</div><div class="text-lg">${format('debt_ratio', fh.debt_ratio, '%')}</div></div>
                     </div>
                 </div>
            `;
}

function renderNaspickScore(data) {
    const stats = data.stats_bar || { fundamentals: 0, value: 0, momentum: 0, stability: 0, risk: 0, consensus: 0 };
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
                     ${['Fundamentals', 'Value', 'Momentum', 'Stability', 'Risk', 'Consensus'].map(k => {
        const key = k.toLowerCase();
        const val = stats[key] || 0;
        return `
                             <div>
                                 <div class="flex justify-between text-xs mb-1.5">
                                     <span class="text-gray-300 font-bold">${k}</span>
                                     <span class="text-blue-400 font-bold">${val}%</span>
                                 </div>
                                 <div class="w-full bg-gray-700 h-2 rounded-full overflow-hidden">
                                     <div class="bg-blue-500 h-full" style="width: ${val}%"></div>
                                 </div>
                             </div>
                         `;
    }).join('')}
                 </div>
            `;
}

function renderTechnical(data) {
    const ta = data.technical_analysis || {};
    const rsi = ta.rsi || { value: 50, status: 'neutral' };
    const rsiColor = rsi.status === 'overbought' ? 'text-red-400' : rsi.status === 'oversold' ? 'text-blue-400' : 'text-gray-400';

    return `
                 <h3 class="flex items-center gap-2 text-sm font-bold text-gray-200 mb-4 border-b border-gray-700 pb-2">기술적 분석</h3>
                 <div class="space-y-4">
                     <!-- RSI -->
                     <div class="bg-[#1e1e24] rounded-lg p-3 border border-gray-700">
                         <div class="flex justify-between items-center mb-3">
                             <div class="text-[10px] text-gray-500 uppercase tracking-wider">RSI (14)</div>
                             <div class="${rsiColor} text-xs font-bold">${rsi.status}</div>
                         </div>
                         <div class="relative h-3 rounded-full overflow-hidden flex bg-gray-800">
                             <div class="absolute top-0 h-3 w-1 bg-white" style="left: ${rsi.value}%"></div>
                             <div class="w-full h-full bg-gradient-to-r from-blue-500 via-gray-600 to-red-500 opacity-50"></div>
                         </div>
                         <div class="text-center mt-2 text-2xl font-bold ${rsiColor}">${rsi.value}</div>
                     </div>
                 </div>
             `;
}

function renderCalendar(data) {
    const cal = data.calendar || {};
    const next = cal.next_earnings || '미정';
    return `
                 <div class="bg-[#282830] rounded-xl border border-gray-800 p-5">
                    <h4 class="text-sm font-bold text-gray-200 mb-4 border-b border-gray-700 pb-2">투자 캘린더</h4>
                    <div class="text-sm">
                        <div class="flex justify-between mb-2">
                            <span class="text-gray-400">다음 실적</span>
                            <span class="text-white font-bold">${next}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-400">배당 수익률</span>
                            <span class="text-white font-bold">${cal.dividend_yield || '-'}%</span>
                        </div>
                    </div>
                 </div>
             `;
}

function renderRelatedStocks(data, allData) {
    // Filter and map logic here
    const peers = data.related_peers || [];

    return `
                 <div class="bg-[#23232a] rounded-xl border border-gray-800 p-5">
                     <h4 class="text-sm font-bold text-gray-200 mb-4 border-b border-gray-700 pb-2">관련 종목</h4>
                     <div class="space-y-3">
                         ${peers.map(p => {
        return `
                                 <a href="/stock/${p.ticker}" class="flex justify-between items-center border-b border-gray-800 pb-2 last:border-0 hover:bg-gray-800 p-2 rounded transition block text-inherit hover:no-underline">
                                     <span class="text-sm font-bold text-white">${p.ticker}</span>
                                     <span class="${p.change_pct >= 0 ? 'text-green-400' : 'text-red-400'} text-sm font-bold">${p.change_pct}%</span>
                                 </a>
                             `;
    }).join('')}
                     </div>
                 </div>
            `;
}

function renderPage(data) {
    console.log("Rendering page for:", data.ticker);
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
    const relatedHtml = safeRender((d) => renderRelatedStocks(d, window.allData), data, "관련 종목");

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
                            <h3 class="flex items-center gap-2 text-sm font-bold text-gray-200 mb-4 border-b border-gray-700 pb-2">재무 건전성 점검</h3>
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
