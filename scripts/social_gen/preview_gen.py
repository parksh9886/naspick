
import os
import json
import base64
import io
import math
from datetime import datetime, timedelta
from jinja2 import Environment, FileSystemLoader
import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
import http.server
import socketserver
import webbrowser
import threading

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # scripts/social_gen
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR)) # Naspick
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
PREVIEW_DIR = os.path.join(BASE_DIR, 'preview')

os.makedirs(PREVIEW_DIR, exist_ok=True)

def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return [] if filename == 'data.json' else {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_style_css():
    path = os.path.join(ASSETS_DIR, 'style.css')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def calculate_technical_indicators(ticker):
    try:
        df = yf.Ticker(ticker).history(period="3mo")
        if len(df) < 26: return None
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        return df
    except: return None

def get_real_data():
    stocks = load_json('data.json')
    calendar = load_json('calendar_data.json')
    today = datetime.now()
    date_str = today.strftime("%Y.%m.%d")
    
    # 1. League Flux
    new_entries = []
    relegated = []
    for s in stocks:
        curr = s.get('rank', 999)
        change = s.get('rank_change', 0)
        prev = curr + change
        if curr <= 25 and prev > 25: new_entries.append(s)
        if curr > 25 and prev <= 25: relegated.append(s)
    new_entries.sort(key=lambda x: x['rank'])
    
    # 2. Oversold
    oversold_opportunities = []
    top_25 = [s for s in stocks if s.get('rank', 999) <= 25]
    for s in top_25:
        rsi_val = s.get('technical_analysis', {}).get('rsi', {}).get('value')
        if rsi_val and rsi_val < 30:
             oversold_opportunities.append({
                 "ticker": s['ticker'],
                 "name": s.get('name', ''),
                 "rank": s['rank'],
                 "rsi": round(rsi_val, 1),
                 "change": s.get('change_pct', 0)
             })
    oversold_opportunities.sort(key=lambda x: x['rsi'])
    oversold_opportunities = oversold_opportunities[:8]
    
    # 3. Golden Cross
    golden_cross_candidates = []
    for s in stocks[:500]: 
        ticker = s['ticker']
        df = calculate_technical_indicators(ticker)
        if df is not None:
            last = df.iloc[-1]
            prev = df.iloc[-2]
            if (prev['MACD'] < prev['Signal']) and (last['MACD'] > last['Signal']):
                golden_cross_candidates.append({
                    "ticker": ticker,
                    "name": s.get('name', ''),
                    "rank": s['rank']
                })
    golden_cross_candidates.sort(key=lambda x: x['rank'])
    golden_cross_candidates = golden_cross_candidates[:8]
    
    # 4. Bullish Candles
    bullish_signals = []
    P_MAP = {
        'Bullish Engulfing': '상승 장악형', 'Hammer': '망치형', 
        'Morning Star': '샛별형', 'Shooting Star': '유성형',
        'Evening Star': '저녁별형', 'Bearish Engulfing': '하락 장악형'
    }
    
    def get_candle_b64(filename):
        path = os.path.join(PROJECT_ROOT, 'images', 'candle_patterns', filename)
        if os.path.exists(path):
            with open(path, "rb") as f:
                return "data:image/png;base64," + base64.b64encode(f.read()).decode('utf-8')
        return ""

    for s in stocks:
        pat = s.get('technical_analysis', {}).get('candle_pattern')
        if pat and pat.get('signal') == 'bullish': 
            p_name_en = pat.get('name_en', 'Bullish')
            p_filename = p_name_en.lower().replace(' ', '_') + ".png"
            bullish_signals.append({
                "ticker": s['ticker'],
                "name": s.get('name', ''),
                "pattern": P_MAP.get(p_name_en, p_name_en),
                "pattern_img": get_candle_b64(p_filename),
                "rank": s['rank']
            })
    bullish_signals.sort(key=lambda x: x['rank'])
    bullish_signals = bullish_signals[:8]
    
    # 5. Earnings
    stock_map = {s['ticker']: s.get('name', '') for s in stocks}
    recent = []
    for ticker, info in calendar.items():
        if info.get('last_earnings_date'):
            try:
                l_date = datetime.strptime(info['last_earnings_date'], "%Y-%m-%d")
                if (today - l_date).days <= 3:
                     recent.append({
                         "ticker": ticker,
                         "name": stock_map.get(ticker, ''),
                         "surprise": info.get('last_surprise', 0),
                         "date": l_date
                     })
            except: pass
    recent.sort(key=lambda x: x['date'], reverse=True)
    
    upcoming = []
    for ticker, info in calendar.items():
         if info.get('next_earnings'):
            try:
                n_date = datetime.strptime(info['next_earnings'], "%Y-%m-%d")
                days = (n_date - today).days
                if 0 <= days <= 7:
                    upcoming.append({
                        "ticker": ticker,
                        "name": stock_map.get(ticker, ''),
                        "d_day": f"D-{days}" if days > 0 else "D-Day",
                        "date": n_date
                    })
            except: pass
    upcoming.sort(key=lambda x: x['date'])

    return {
        "date_string": date_str,
        "league_flux": {"in": new_entries, "out": relegated},
        "oversold": oversold_opportunities,
        "golden_cross": golden_cross_candidates,
        "bullish_candles": bullish_signals,
        "earnings": {"recent": recent[:3], "upcoming": upcoming[:3]}
    }

def chunk_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def generate_preview():
    print("🚀 Generating Preview HTMLs...")
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    style_css = get_style_css()
    data = get_real_data()
    
    # Earnings pagination (max 5 per side per page)
    earnings_slides = []
    recent_all = data['earnings']['recent']
    upcoming_all = data['earnings']['upcoming']
    max_items = max(len(recent_all), len(upcoming_all))
    
    if max_items == 0:
        # No earnings data at all
        earnings_slides.append(("05_calendar.html", "06_earnings.html", {
            "slide_title": "📊 실적발표! 서프라이즈?",
            "recent": [],
            "upcoming": []
        }))
    else:
        pages_needed = (max_items + 4) // 5  # Ceiling division
        for page in range(pages_needed):
            idx_str = "" if pages_needed == 1 else f" ({page+1}/{pages_needed})"
            fname = "06_earnings.html" if page == 0 else f"06_earnings_{page+1}.html"
            
            recent_chunk = recent_all[page*5 : (page+1)*5]
            upcoming_chunk = upcoming_all[page*5 : (page+1)*5]
            
            earnings_slides.append(("05_calendar.html", fname, {
                "slide_title": "📊 실적발표! 서프라이즈?" + idx_str,
                "recent": recent_chunk,
                "upcoming": upcoming_chunk
            }))
    
    base_slides = [
        ("01_cover.html", "01_cover.html", {}),
        ("06_cta.html", "07_cta.html", {
            "slide_title": "NEXT LEVEL INVESTING"
        })
    ]
    
    # Pagination Logic
    tier_paginated = []
    in_flux = data['league_flux']['in']
    out_flux = data['league_flux']['out']
    max_len = max(len(in_flux), len(out_flux))
    
    if max_len == 0:
        tier_paginated.append(("02_tier.html", "02_tier.html", {
            "slide_title": "👑 NEW 1티어, 왕좌의 교체",
            "in_stocks": [], "out_stocks": []
        }))
    else:
        chunks_count = (max_len + 3) // 4
        for i in range(chunks_count):
            idx_str = "" if chunks_count == 1 else f" ({i+1}/{chunks_count})"
            fname = "02_tier.html" if i == 0 else f"02_tier_{i+1}.html"
            tier_paginated.append(("02_tier.html", fname, {
                "slide_title": "👑 NEW 1티어, 왕좌의 교체" + idx_str,
                "in_stocks": in_flux[i*4 : (i+1)*4],
                "out_stocks": out_flux[i*4 : (i+1)*4]
            }))
            
    paginated_types = [
        ('oversold', '03_oversold.html', '03_oversold', "📉 지금이 줍줍 찬스?!", "RSI < 30 (과매도) 진입한 1티어", "oversold"),
        ('golden_cross', '04_golden.html', '04_golden', "🚀 돈 들어왔다! 골든크로스", "MACD 골든크로스 발생한 상승 전환 종목", "list"),
        ('bullish_candles', '04_golden.html', '05_candles', "🕯️ 상승 시그널 떴다!", "강력한 상승 반전형 캔들 패턴 포착", "candle")
    ]
    
    final_slides = []
    for key, tmpl, prefix, title, subtitle, mode in paginated_types:
        items = data[key]
        chunks = list(chunk_list(items, 4))
        if not chunks:
             final_slides.append((tmpl, f"{prefix}.html", {
                "slide_title": title, "subtitle": subtitle, "items": [], "mode": mode
            }))
        else:
            for i, chunk in enumerate(chunks):
                idx_str = "" if len(chunks) == 1 else f" ({i+1}/{len(chunks)})"
                fname = f"{prefix}.html" if i == 0 else f"{prefix}_{i+1}.html"
                final_slides.append((tmpl, fname, {
                    "slide_title": title + idx_str, "subtitle": subtitle, "items": chunk, "mode": mode
                }))

    ordered = []
    ordered.append(base_slides[0]) # Cover
    for tp in tier_paginated: ordered.append(tp)
    for fs in final_slides: 
        if "oversold" in fs[1]: ordered.append(fs)
    for fs in final_slides: 
        if "golden" in fs[1]: ordered.append(fs)
    for fs in final_slides: 
        if "candles" in fs[1]: ordered.append(fs)
    for es in earnings_slides: ordered.append(es)  # Earnings (paginated)
    ordered.append(base_slides[1]) # CTA

    # Generate Pages
    preview_links = []
    for tmpl_name, out_name, ctx in ordered:
        full_ctx = {"style_css": style_css, "date_string": data['date_string'], **ctx}
        content = env.get_template(tmpl_name).render(full_ctx)
        
        # Inject standard style just in case
        if "https://cdn.tailwindcss.com" not in content:
             pass # Assumed template has it
             
        out_path = os.path.join(PREVIEW_DIR, out_name)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(content)
        preview_links.append(out_name)
        print(f"✅ Generated {out_name}")

    # Generate Dashboard
    index_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Naspick Design Preview</title>
        <style>
            body { font-family: sans-serif; background: #111; color: white; display: flex; margin: 0; height: 100vh; }
            #sidebar { width: 250px; background: #222; padding: 20px; border-right: 1px solid #333; overflow-y: auto; }
            #content { flex: 1; display: flex; justify-content: center; align-items: center; background: #000; }
            iframe { width: 1080px; height: 1080px; border: none; transform: scale(0.8); transform-origin: center; background: white; }
            a { display: block; padding: 10px; color: #aaa; text-decoration: none; border-bottom: 1px solid #333; cursor: pointer; }
            a:hover, a.active { color: #38bdf8; background: #333; }
        </style>
        <script>
            function setFrame(url, el) {
                document.getElementById('preview-frame').src = url;
                document.querySelectorAll('a').forEach(a => a.classList.remove('active'));
                el.classList.add('active');
            }
        </script>
    </head>
    <body>
        <div id="sidebar">
            <h2 style="color:#38bdf8; margin-top:0;">Naspick Slides</h2>
    """
    for link in preview_links:
        name = link.replace('.html', '').replace('_', ' ').title()
        index_html += f'<a onclick="setFrame(\'{link}\', this)">{name}</a>'
    
    index_html += """
        <div style="margin-top: 20px; border-top: 1px solid #333; padding-top: 20px;">
            <a href="/refresh" style="color: #4ade80; border: 1px solid #4ade80; text-align: center; border-radius: 4px;">⚡ Refresh All</a>
        </div>
        </div>
        <div id="content">
            <iframe id="preview-frame" src="01_cover.html"></iframe>
        </div>
    </body>
    </html>
    """
    
    with open(os.path.join(PREVIEW_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_html)
        
    print("✨ Preview dashboard generated at index.html")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PREVIEW_DIR, **kwargs)

    def do_GET(self):
        if self.path == '/refresh':
            print("🔄 Refreshing templates...")
            generate_preview()
            self.send_response(302)
            self.send_header('Location', '/index.html')
            self.end_headers()
            return
        super().do_GET()

def start_server():
    PORT = 8000
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"\n🌍 Serving at http://localhost:{PORT}")
        print("Press Ctrl+C to stop")
        httpd.serve_forever()

if __name__ == "__main__":
    generate_preview()
    # Simple check if port is busy? Just try.
    try:
        start_server()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Server error: {e}")
