
import asyncio
import os
import json
import base64
import io
import nest_asyncio
from datetime import datetime, timedelta
from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright
import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
import requests

# Apply nest_asyncio
nest_asyncio.apply()

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # scripts/social_gen
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR)) # Naspick
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')

os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        print(f"⚠️ Warning: {filename} not found at {path}")
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
    """Fetch history and calculate MACD, RSI for Golden Cross/Oversold check"""
    try:
        df = yf.Ticker(ticker).history(period="3mo")
        if len(df) < 26:
            return None

        # RSI (14)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # MACD (12, 26, 9)
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        return df
    except Exception as e:
        print(f"❌ Tech calc failed for {ticker}: {e}")
        return None

def get_real_data():
    stocks = load_json('data.json')
    calendar = load_json('calendar_data.json')
    today = datetime.now()
    date_str = today.strftime("%Y.%m.%d")
    
    # ---------------------------------------------------------
    # Slide 1: LeagueFlux (Changes in Top 25)
    # ---------------------------------------------------------
    new_entries = []
    relegated = []
    
    for s in stocks:
        curr = s.get('rank', 999)
        change = s.get('rank_change', 0)
        prev = curr + change 
        
        if curr <= 25 and prev > 25:
            new_entries.append(s)
        if curr > 25 and prev <= 25:
            relegated.append(s)
            
    new_entries.sort(key=lambda x: x['rank'])
    
    # ---------------------------------------------------------
    # Slide 2: Oversold Tier 1 (RSI < 30 in Top 25)
    # ---------------------------------------------------------
    oversold_opportunities = []
    top_25_stocks = [s for s in stocks if s.get('rank', 999) <= 25]
    
    for s in top_25_stocks:
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
    
    # ---------------------------------------------------------
    # Slide 3: Golden Cross (Volume + MACD)
    # ---------------------------------------------------------
    golden_cross_candidates = []
    
    # Scan Top 500 for efficiency
    # [OPTIMIZATION] Use pre-calculated signals from Engine (data.json)
    # This avoids 500+ API calls and prevents "Too Many Requests" errors
    print("⏳ Scanning Golden Cross from pre-calculated data...")
    stock_map_rank = {s['ticker']: s['rank'] for s in stocks}
    
    for s in stocks:
        # Engine already calculates MACD Golden Cross and puts it in signals list
        if "MACD_GoldenCross" in s.get('signals', []):
            golden_cross_candidates.append({
                "ticker": s['ticker'],
                "name": s.get('name', ''),
                "rank": s['rank']
            })
    
    golden_cross_candidates.sort(key=lambda x: x['rank'])
    golden_cross_candidates = golden_cross_candidates[:8]
    
    # ---------------------------------------------------------
    # Slide 4: Bullish Candles
    # ---------------------------------------------------------
    bullish_signals = []
    
    # Pattern Mapping
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
    
    # ---------------------------------------------------------
    # Slide 5: Earnings
    # ---------------------------------------------------------
    stock_map = {s['ticker']: s.get('name', '') for s in stocks}
    recent = []
    
    for ticker, info in calendar.items():
        if info.get('last_earnings_date'):
            try:
                l_date = datetime.strptime(info['last_earnings_date'], "%Y-%m-%d")
                if (today - l_date).days <= 3: # 3 days window
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
                # [User Request] Limit to Today, Tomorrow, Day after tomorrow (3 days)
                if 0 <= days <= 2: 
                    upcoming.append({
                        "ticker": ticker,
                        "name": stock_map.get(ticker, ''),
                        "d_day": f"D-{days}" if days > 0 else "D-Day",
                        "date": n_date
                    })
            except: pass
            
    upcoming.sort(key=lambda x: x['date'])
    # [User Request] Limit to max 10 items
    upcoming = upcoming[:10]

    return {
        "date_string": date_str,
        "league_flux": {"in": new_entries, "out": relegated},
        "oversold": oversold_opportunities,
        "golden_cross": golden_cross_candidates,
        "bullish_candles": bullish_signals,
        "earnings": {"recent": recent, "upcoming": upcoming} # Pass ALL for pagination
    }

def chunk_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

async def generate_images():
    print(f"🚀 Generating Premium Briefing (Top 25 Mode)...")
    
    # NEW: Clean output directory first to prevent stale images
    for f in os.listdir(OUTPUT_DIR):
        if f.endswith(".png"):
            os.remove(os.path.join(OUTPUT_DIR, f))
    print(f"🧹 Output directory cleaned.")
    
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    style_css = get_style_css()
    data = get_real_data()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1080, "height": 1080}, device_scale_factor=2)
        
        base_slides = [
            ("01_cover.html", "01_cover.png", {}),
            ("06_cta.html", "07_cta.png", {
                "slide_title": "NEXT LEVEL INVESTING"
            })
        ]
        
        # 1. Tier Flux Pagination
        tier_paginated = []
        in_flux = data['league_flux']['in']
        out_flux = data['league_flux']['out']
        max_len = max(len(in_flux), len(out_flux))
        
        if max_len == 0:
            tier_paginated.append(("02_tier.html", "02_tier.png", {
                "slide_title": "👑 NEW 1티어, 왕좌의 교체",
                "in_stocks": [], "out_stocks": []
            }))
        else:
            chunks_count = (max_len + 3) // 4
            for i in range(chunks_count):
                idx_str = "" if chunks_count == 1 else f" ({i+1}/{chunks_count})"
                fname = "02_tier.png" if i == 0 else f"02_tier_{i+1}.png"
                
                tier_paginated.append(("02_tier.html", fname, {
                    "slide_title": "👑 NEW 1티어, 왕좌의 교체" + idx_str,
                    "in_stocks": in_flux[i*4 : (i+1)*4],
                    "out_stocks": out_flux[i*4 : (i+1)*4]
                }))

        # 2. Content Slides (Oversold, Golden, Candles)
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
                 final_slides.append((tmpl, f"{prefix}.png", {
                    "slide_title": title, "subtitle": subtitle, "items": [], "mode": mode
                }))
            else:
                for i, chunk in enumerate(chunks):
                    idx_str = "" if len(chunks) == 1 else f" ({i+1}/{len(chunks)})"
                    fname = f"{prefix}.png" if i == 0 else f"{prefix}_{i+1}.png"
                    
                    final_slides.append((tmpl, fname, {
                        "slide_title": title + idx_str, "subtitle": subtitle, "items": chunk, "mode": mode
                    }))
                    
        # 3. Earnings Pagination
        earnings_slides = []
        recent_all = data['earnings']['recent']
        upcoming_all = data['earnings']['upcoming']
        max_items = max(len(recent_all), len(upcoming_all))
        
        if max_items == 0:
            earnings_slides.append(("05_calendar.html", "06_earnings.png", {
                "slide_title": "📊 실적발표! 서프라이즈?",
                "recent": [],
                "upcoming": []
            }))
        else:
            pages_needed = (max_items + 4) // 5 
            for page_idx in range(pages_needed):
                idx_str = "" if pages_needed == 1 else f" ({page_idx+1}/{pages_needed})"
                fname = "06_earnings.png" if page_idx == 0 else f"06_earnings_{page_idx+1}.png"
                
                recent_chunk = recent_all[page_idx*5 : (page_idx+1)*5]
                upcoming_chunk = upcoming_all[page_idx*5 : (page_idx+1)*5]
                
                earnings_slides.append(("05_calendar.html", fname, {
                    "slide_title": "📊 실적발표! 서프라이즈?" + idx_str,
                    "recent": recent_chunk,
                    "upcoming": upcoming_chunk
                }))

        # Re-construct orderly list
        ordered = []
        ordered.append(base_slides[0]) # Cover
        
        for tp in tier_paginated: ordered.append(tp)
        for fs in final_slides: 
            if "oversold" in fs[1]: ordered.append(fs)
        for fs in final_slides: 
            if "golden" in fs[1]: ordered.append(fs)
        for fs in final_slides: 
            if "candles" in fs[1]: ordered.append(fs)
        for es in earnings_slides: ordered.append(es)
        
        ordered.append(base_slides[1]) # CTA
        
        for template_name, output_name, ctx in ordered:
            print(f"📸 {output_name}...")
            full_ctx = {
                "style_css": style_css, 
                "date_string": data['date_string'],
                **ctx
            }
            try:
                content = env.get_template(template_name).render(full_ctx)
                # Inject tailwind if missing (safety net)
                if "cdn.tailwindcss.com" not in content:
                    content = content.replace("<head>", "<head><script src='https://cdn.tailwindcss.com'></script>")
                    
                await page.set_content(content)
                await page.wait_for_timeout(200)
                await page.screenshot(path=os.path.join(OUTPUT_DIR, output_name), type='png')
            except Exception as e:
                print(f"❌ Failed to generate {output_name}: {e}")
            
        await browser.close()
        print("✅ Generation Complete.")

if __name__ == "__main__":
    asyncio.run(generate_images())

