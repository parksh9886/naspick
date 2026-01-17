"""
Sitemap Generator for Naspick
Generates sitemap.xml with current date, stock pages, and sector pages
"""
import json
import datetime
import os

BASE_URL = "https://naspick.com"

# Sector mapping (Korean to URL slug)
SECTOR_SLUGS = {
    "기술": "technology",
    "커뮤니케이션": "communication",
    "임의소비재": "consumer-discretionary",
    "필수소비재": "consumer-staples",
    "에너지": "energy",
    "금융": "financials",
    "헬스케어": "healthcare",
    "산업재": "industrials",
    "소재": "materials",
    "부동산": "real-estate",
    "유틸리티": "utilities"
}

def generate_sitemap():
    print("🗺️ Generating Sitemap...")

    # Get correct data path relative to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    data_path = os.path.join(project_root, 'data', 'data.json')
    
    # Fallback for running from project root
    if not os.path.exists(data_path):
        data_path = 'data/data.json'
    
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ data.json not found at {data_path}")
        return

    today = datetime.date.today().isoformat()
    
    xml_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        '',
        '    <!-- Homepage -->',
        '    <url>',
        f'        <loc>{BASE_URL}/</loc>',
        f'        <lastmod>{today}</lastmod>',
        '        <changefreq>daily</changefreq>',
        '        <priority>1.0</priority>',
        '    </url>',
    ]

    # Sector pages
    xml_parts.append('')
    xml_parts.append('    <!-- Sector Pages -->')
    for sector_kr, sector_slug in SECTOR_SLUGS.items():
        xml_parts.extend([
            '    <url>',
            f'        <loc>{BASE_URL}/sector/{sector_slug}</loc>',
            f'        <lastmod>{today}</lastmod>',
            '        <changefreq>daily</changefreq>',
            '        <priority>0.9</priority>',
            '    </url>',
        ])

    # Stock pages
    xml_parts.append('')
    xml_parts.append('    <!-- Stock Pages -->')
    for item in data:
        ticker = item.get('ticker')
        if ticker:
            xml_parts.extend([
                '    <url>',
                f'        <loc>{BASE_URL}/stock/{ticker}</loc>',
                f'        <lastmod>{today}</lastmod>',
                '        <changefreq>daily</changefreq>',
                '        <priority>0.8</priority>',
                '    </url>',
            ])

    xml_parts.append('</urlset>')

    # Write sitemap
    sitemap_path = os.path.join(project_root, 'sitemap.xml') if 'project_root' in dir() else 'sitemap.xml'
    if os.path.exists(os.path.join(project_root, 'sitemap.xml')):
        sitemap_path = os.path.join(project_root, 'sitemap.xml')
    else:
        sitemap_path = 'sitemap.xml'
        
    with open(sitemap_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(xml_parts))
    
    print(f"✅ Sitemap generated: {len(data)} stocks + {len(SECTOR_SLUGS)} sectors")
    print(f"   Updated: {today}")

if __name__ == "__main__":
    generate_sitemap()
