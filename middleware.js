import { next } from '@vercel/edge';

export const config = {
    matcher: '/stock/:ticker*',
};

export default async function middleware(request) {
    const url = new URL(request.url);
    const pathParts = url.pathname.split('/');
    const ticker = pathParts[2]?.toUpperCase();

    if (!ticker) {
        return next();
    }

    // Fetch the original page
    const response = await fetch(request);
    const html = await response.text();

    // Get today's date in Korean timezone
    const now = new Date();
    const koreaTime = new Date(now.toLocaleString('en-US', { timeZone: 'Asia/Seoul' }));
    const month = koreaTime.getMonth() + 1;
    const date = koreaTime.getDate();
    const dateString = `${month}월 ${date}일`;

    // Replace the default title and meta description with date-stamped versions
    let modifiedHtml = html;

    // Update title
    modifiedHtml = modifiedHtml.replace(
        /<title>종목 상세페이지:나스픽<\/title>/,
        `<title>${dateString} ${ticker} 실시간 티어 & 주가 분석 | 나스픽</title>`
    );

    // Update meta description
    modifiedHtml = modifiedHtml.replace(
        /<meta name="description" content="미국 주식 실시간 티어 분석 정보">/,
        `<meta name="description" content="[${dateString} 기준] ${ticker} AI 정밀 분석. 나스픽 점수와 티어 확인. 기관 수급 포착 및 모멘텀 분석.">`
    );

    // Update OG title
    modifiedHtml = modifiedHtml.replace(
        /<meta property="og:title" content="종목 상세페이지 \| 나스픽">/,
        `<meta property="og:title" content="${dateString} ${ticker} 실시간 티어 & 주가 분석 | 나스픽">`
    );

    // Update OG description
    modifiedHtml = modifiedHtml.replace(
        /<meta property="og:description" content="미국 주식 실시간 티어 분석 정보">/,
        `<meta property="og:description" content="[${dateString} 기준] ${ticker} AI 정밀 분석. 나스픽 점수와 티어 확인.">`
    );

    // Update Twitter title
    modifiedHtml = modifiedHtml.replace(
        /<meta name="twitter:title" content="종목 상세페이지 \| 나스픽">/,
        `<meta name="twitter:title" content="${dateString} ${ticker} 실시간 티어 & 주가 분석 | 나스픽">`
    );

    // Update Twitter description
    modifiedHtml = modifiedHtml.replace(
        /<meta name="twitter:description" content="미국 주식 실시간 티어 분석 정보">/,
        `<meta name="twitter:description" content="[${dateString} 기준] ${ticker} AI 정밀 분석.">`
    );

    return new Response(modifiedHtml, {
        status: response.status,
        headers: {
            'content-type': 'text/html;charset=UTF-8',
        },
    });
}
