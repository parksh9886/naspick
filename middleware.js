export const config = {
    matcher: '/stock/:ticker*',
};

export default async function middleware(request) {
    const url = new URL(request.url);
    const pathParts = url.pathname.split('/');
    const ticker = pathParts[2]?.toUpperCase();

    if (!ticker) {
        return;
    }

    // Get today's date in Korean timezone
    const now = new Date();
    const koreaTime = new Date(now.toLocaleString('en-US', { timeZone: 'Asia/Seoul' }));
    const month = koreaTime.getMonth() + 1;
    const date = koreaTime.getDate();
    const dateString = `${month}월 ${date}일`;

    // Fetch the original page
    const originUrl = new URL('/page.html', request.url);
    const response = await fetch(originUrl);
    const html = await response.text();

    // Replace the default title and meta description with date-stamped versions
    let modifiedHtml = html;

    // Update title - SEO optimized
    modifiedHtml = modifiedHtml.replace(
        /<title>종목 상세페이지:나스픽<\/title>/,
        `<title>${dateString} ${ticker} 주가 전망 및 AI 분석 | 나스픽</title>`
    );

    // Update meta description - SEO optimized with high-volume keywords
    modifiedHtml = modifiedHtml.replace(
        /<meta name="description" content="미국 주식 실시간 티어 분석 정보">/,
        `<meta name="description" content="[${dateString}] ${ticker} 주가 전망, 목표가, 실시간 AI 분석. 나스픽 점수와 티어 확인. 재무건전성, RSI, 상승여력 분석.">`
    );

    // Update OG title
    modifiedHtml = modifiedHtml.replace(
        /<meta property="og:title" content="종목 상세페이지 \| 나스픽">/,
        `<meta property="og:title" content="${dateString} ${ticker} 주가 전망 및 AI 분석 | 나스픽">`
    );

    // Update OG description
    modifiedHtml = modifiedHtml.replace(
        /<meta property="og:description" content="미국 주식 실시간 티어 분석 정보">/,
        `<meta property="og:description" content="[${dateString}] ${ticker} 주가 전망과 목표가 분석. 나스픽 AI 점수 확인.">`
    );

    // Update Twitter title
    modifiedHtml = modifiedHtml.replace(
        /<meta name="twitter:title" content="종목 상세페이지 \| 나스픽">/,
        `<meta name="twitter:title" content="${dateString} ${ticker} 주가 전망 및 AI 분석 | 나스픽">`
    );

    // Update Twitter description
    modifiedHtml = modifiedHtml.replace(
        /<meta name="twitter:description" content="미국 주식 실시간 티어 분석 정보">/,
        `<meta name="twitter:description" content="[${dateString}] ${ticker} AI 분석. 주가 전망과 목표가 확인.">`
    );

    return new Response(modifiedHtml, {
        status: 200,
        headers: {
            'content-type': 'text/html;charset=UTF-8',
        },
    });
}
