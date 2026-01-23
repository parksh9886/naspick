
import json
import os
import shutil
from datetime import datetime

# Configuration
DATA_PATH = os.path.join("data", "data.json")
TEMPLATE_KO = "page.html"
TEMPLATE_EN = os.path.join("en", "page.html")
OUTPUT_DIR = "."  # Root directory

SECTOR_SLUGS = {
    "Technology": "technology",
    "Communication Services": "communication-services",
    "Consumer Cyclical": "consumer-cyclical",
    "Financial Services": "financial-services",
    "Healthcare": "healthcare",
    "Industrials": "industrials",
    "Consumer Defensive": "consumer-defensive",
    "Energy": "energy",
    "Basic Materials": "basic-materials",
    "Real Estate": "real-estate",
    "Utilities": "utilities"
}

SECTOR_NAMES_KO = {
    "Technology": "기술",
    "Communication Services": "커뮤니케이션",
    "Consumer Cyclical": "임의소비재",
    "Financial Services": "금융",
    "Healthcare": "헬스케어",
    "Industrials": "산업재",
    "Consumer Defensive": "필수소비재",
    "Energy": "에너지",
    "Basic Materials": "소재",
    "Real Estate": "부동산",
    "Utilities": "유틸리티"
}

def load_data():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def replace_meta_tags(content, meta):
    """
    Replaces meta tag placeholders with actual values.
    Currently uses simple string replacement for known placeholders or regex could be used.
    Since we know the exact lines from the template, we can act intelligently.
    However, the template has hardcoded default values. We will replace them.
    """
    # Common replacements
    content = content.replace('<title>종목 상세페이지:나스픽</title>', f'<title>{meta["title"]}</title>')
    content = content.replace('<title>Stock Analysis | NASPICK</title>', f'<title>{meta["title"]}</title>')
    
    # Description
    content = content.replace('content="미국 주식 실시간 티어 분석 정보"', f'content="{meta["description"]}"')
    content = content.replace('content="AI-powered stock analysis and ratings"', f'content="{meta["description"]}"')
    
    # Canonical & Alternates
    # NOTE: The template has hardcoded URLs like href="https://naspick.com/" in canonical
    # We need to replace the entire lines or be specific.
    
    # KO Template
    content = content.replace('<link rel="canonical" href="https://naspick.com/">', f'<link rel="canonical" href="{meta["url"]}">')
    content = content.replace('<link rel="alternate" hreflang="ko" href="https://naspick.com/">', f'<link rel="alternate" hreflang="ko" href="{meta["url_ko"]}">')
    content = content.replace('<link rel="alternate" hreflang="en" href="https://naspick.com/en/">', f'<link rel="alternate" hreflang="en" href="{meta["url_en"]}">')
    content = content.replace('<link rel="alternate" hreflang="x-default" href="https://naspick.com/en/">', f'<link rel="alternate" hreflang="x-default" href="{meta["url_en"]}">')
    
    # EN Template (Similar defaults)
    content = content.replace('<link rel="canonical" href="https://naspick.com/en/">', f'<link rel="canonical" href="{meta["url"]}">')
    # Note: reusing the replacement logic if strings match exactly
    
    # OG Tags
    content = content.replace('content="종목 상세페이지 | 나스픽"', f'content="{meta["og_title"]}"')
    content = content.replace('content="Stock Analysis | NASPICK"', f'content="{meta["og_title"]}"')
    
    # OG Description (handled by general description replacement usually, but let's be safe if they differ in template)
    # The template uses same string for og:description as meta description, so previous replace likely caught it.
    
    content = content.replace('content="https://naspick.com/"', f'content="{meta["url"]}"')
    content = content.replace('content="https://naspick.com/en/"', f'content="{meta["url"]}"')
    
    # Image Replacements (OG & Twitter)
    if "image" in meta:
        # OG Image string in template
        content = content.replace('content="https://naspick.com/images/og-image.png"', f'content="{meta["image"]}"')
        # Twitter Image string in template (note the path difference in template: /og-image.png vs /images/og-image.png)
        content = content.replace('content="https://naspick.com/og-image.png"', f'content="{meta["image"]}"')
        
    return content

def generate_stock_pages(data):
    # Load Templates
    with open(TEMPLATE_KO, "r", encoding="utf-8") as f:
        template_ko = f.read()
    with open(TEMPLATE_EN, "r", encoding="utf-8") as f:
        template_en = f.read()
        
    today = datetime.now().strftime("%Y-%m-%d")
    
    print(f"Generating {len(data)} stock pages...")
    
    for item in data:
        ticker = item['ticker']
        name_ko = item.get('name', ticker)
        name_en = item.get('name_en', item.get('name', ticker))
        sector = item.get('sector', '')
        
        # 1. Korean Page
        output_dir_ko = os.path.join(OUTPUT_DIR, "stock", ticker)
        ensure_dir(output_dir_ko)
        
        url_ko = f"https://naspick.com/stock/{ticker}"
        url_en = f"https://naspick.com/en/stock/{ticker}"
        
        title_ko = f"{today} {ticker} 주가 전망 & 목표가 | {name_ko} AI 분석 - 나스픽"
        desc_ko = f"[{today}] {name_ko}({ticker}) 적정 주가 및 월스트리트 목표가 분석. AI가 진단한 {name_ko}의 투자 매력도와 실시간 티어 정보를 확인하세요."
        
        meta_ko = {
            "title": title_ko,
            "description": desc_ko,
            "og_title": title_ko,
            "url": url_ko,
            "url_ko": url_ko,
            "url_en": url_en,
            "image": f"https://financialmodelingprep.com/image-stock/{ticker.replace('.', '-')}.png"
        }
        
        html_ko = replace_meta_tags(template_ko, meta_ko)
        
        with open(os.path.join(output_dir_ko, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_ko)
            
        # 2. English Page
        output_dir_en = os.path.join(OUTPUT_DIR, "en", "stock", ticker)
        ensure_dir(output_dir_en)
        
        title_en = f"{ticker} Stock Price Forecast & Target | {name_en} AI Analysis - NASPICK"
        desc_en = f"[{today}] {name_en} ({ticker}) stock price target and AI analysis. Check {name_en}'s investment rating and real-time tier score."
        
        meta_en = {
            "title": title_en,
            "description": desc_en,
            "og_title": title_en,
            "url": url_en,
            "url_ko": url_ko,
            "url_en": url_en,
            "image": f"https://financialmodelingprep.com/image-stock/{ticker.replace('.', '-')}.png"
        }
        
        html_en = replace_meta_tags(template_en, meta_en)
        
        with open(os.path.join(output_dir_en, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_en)

def main():
    print("Starting Static Site Generation...")
    try:
        data = load_data()
        generate_stock_pages(data)
        print("Successfully generated static pages.")
    except Exception as e:
        print(f"Error during SSG: {e}")

if __name__ == "__main__":
    main()
