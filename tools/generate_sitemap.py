import json
import datetime
import os

# 1. 사이트 기본 주소 (본인 도메인으로 변경 필수!)
BASE_URL = "https://naspick.com"

def generate_sitemap():
    print("🗺️ Generating Sitemap & Robots.txt...")

    # 2. 종목 데이터 읽기
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ data.json not found!")
        return

    # 3. XML 헤더 작성
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    # 4. 메인 페이지 추가
    today = datetime.date.today().isoformat()
    xml_content += f"""
    <url>
        <loc>{BASE_URL}/index.html</loc>
        <lastmod>{today}</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
    """

    # 5. 각 종목별 상세 페이지 URL 추가 (Clean URL 적용)
    for item in data:
        ticker = item.get('ticker')
        if ticker:
            # 특수문자(&) 처리 (URL 인코딩)
            safe_ticker = ticker.replace("&", "&amp;")
            # Vercel Rewrite 적용된 Clean URL
            url = f"{BASE_URL}/stock/{safe_ticker}"
            
            xml_content += f"""
    <url>
        <loc>{url}</loc>
        <lastmod>{today}</lastmod>
        <changefreq>daily</changefreq>
        <priority>0.8</priority>
    </url>"""

    xml_content += '\n</urlset>'

    # 6. Sitemap 저장
    with open('sitemap.xml', 'w', encoding='utf-8') as f:
        f.write(xml_content)
    
    print(f"✅ Sitemap generated with {len(data) + 1} URLs.")

    # 7. Robots.txt 생성
    robots_content = f"""User-agent: *
Allow: /

Sitemap: {BASE_URL}/sitemap.xml
"""
    with open('robots.txt', 'w', encoding='utf-8') as f:
        f.write(robots_content)
    
    print("✅ robots.txt generated.")

if __name__ == "__main__":
    generate_sitemap()
