export const config = {
    matcher: ['/stock/:ticker*', '/en/stock/:ticker*'],
};

export default async function middleware(request) {
    const url = new URL(request.url);
    const pathParts = url.pathname.split('/');
    const isEn = pathParts[1] === 'en';
    const ticker = (isEn ? pathParts[3] : pathParts[2])?.toUpperCase();

    if (!ticker || ticker === 'PAGE.HTML' || ticker === 'STOCK') {
        return;
    }

    // Fetch the original page
    const templatePath = isEn ? '/en/page.html' : '/page.html';
    const originUrl = new URL(templatePath, request.url);
    const response = await fetch(originUrl);
    const html = await response.text();

    let modifiedHtml = html;

    if (isEn) {
        // EN Replacements
        modifiedHtml = modifiedHtml.replace(
            /<title>Stock Analysis \| NASPICK<\/title>/,
            `<title>${ticker} Stock Forecast & Price Target | AI Analysis - NASPICK</title>`
        );
        modifiedHtml = modifiedHtml.replace(
            /<meta name="description" content="AI-powered stock analysis and ratings">/,
            `<meta name="description" content="${ticker} Stock Price Prediction & AI Analysis. Enter your entry price to see your Top % rank in 5 seconds! Check Wall St. targets and real-time tier instantly.">`
        );
        modifiedHtml = modifiedHtml.replace(
            /<meta property="og:title" content="Stock Analysis \| NASPICK">/,
            `<meta property="og:title" content="${ticker} Stock Forecast & Price Target | AI Analysis - NASPICK">`
        );
        modifiedHtml = modifiedHtml.replace(
            /<meta property="og:description" content="AI-powered stock analysis and ratings">/,
            `<meta property="og:description" content="${ticker} Stock Price Prediction & AI Analysis. Enter your entry price to see your Top % rank in 5 seconds!">`
        );
    } else {
        // KO Replacements
        modifiedHtml = modifiedHtml.replace(
            /<title>종목 상세페이지:나스픽<\/title>/,
            `<title>${ticker} 주가 전망 & 목표가 | AI 분석 - 나스픽</title>`
        );
        modifiedHtml = modifiedHtml.replace(
            /<meta name="description" content="미국 주식 실시간 티어 분석 정보">/,
            `<meta name="description" content="${ticker} 주가 전망 & AI 분석. 내 평단가 입력하면 5초 만에 상위 몇 %인지 진단해 드립니다. 월가 목표가와 비교해보세요.">`
        );
        modifiedHtml = modifiedHtml.replace(
            /<meta property="og:title" content="종목 상세페이지 \| 나스픽">/,
            `<meta property="og:title" content="${ticker} 주가 전망 & 목표가 | AI 분석 - 나스픽">`
        );
        modifiedHtml = modifiedHtml.replace(
            /<meta property="og:description" content="미국 주식 실시간 티어 분석 정보">/,
            `<meta property="og:description" content="${ticker} 주가 전망 & AI 분석. 내 평단가 입력하면 5초 만에 상위 몇 %인지 진단해 드립니다.">`
        );
    }

    return new Response(modifiedHtml, {
        status: 200,
        headers: {
            'content-type': 'text/html;charset=UTF-8',
        },
    });
}
