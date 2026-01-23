import os
import requests
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import matplotlib.pyplot as plt
import io

# Setup Directories
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'temp_images')
os.makedirs(OUTPUT_DIR, exist_ok=True)
FONT_PATH = os.path.join(OUTPUT_DIR, 'NanumGothicBold.ttf')

# Colors
COLOR_BG = "#121212"
COLOR_TEXT_MAIN = "#FFFFFF"
COLOR_TEXT_SUB = "#CCCCCC"
COLOR_ACCENT_RED = "#FF4444"
COLOR_ACCENT_GREEN = "#00FF85"
COLOR_ACCENT_BLUE = "#4F46E5"
COLOR_TIER_GOLD = "#FFD700"
COLOR_CARD_BG = "#1E1E1E"

def download_font():
    if not os.path.exists(FONT_PATH):
        print("Downloading font...")
        url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Bold.ttf"
        r = requests.get(url)
        with open(FONT_PATH, 'wb') as f:
            f.write(r.content)

def create_base_image(height=1350):
    img = Image.new('RGB', (1080, height), COLOR_BG)
    draw = ImageDraw.Draw(img)
    return img, draw

def draw_header_footer(draw, slide_title):
    # Header
    font_header = ImageFont.truetype(FONT_PATH, 40)
    draw.text((50, 50), "Naspick Daily Briefing", font=font_header, fill=COLOR_ACCENT_BLUE)
    draw.text((50, 100), slide_title, font=font_header, fill=COLOR_TEXT_SUB)
    
    # Footer
    font_footer = ImageFont.truetype(FONT_PATH, 30)
    draw.text((50, 1280), "Powered by Naspick AI", font=font_footer, fill="#555555")
    draw.text((850, 1280), datetime.now().strftime("%Y.%m.%d"), font=font_footer, fill="#555555")

# 1. Cover
def create_cover():
    img, draw = create_base_image()
    font_title = ImageFont.truetype(FONT_PATH, 80)
    font_sub = ImageFont.truetype(FONT_PATH, 50)
    
    # Title
    draw.text((100, 400), "오늘 밤,\n세력들이 매집하는\n미국주식 4선", font=font_title, fill=COLOR_TEXT_MAIN, spacing=20)
    
    # Date Pill
    draw.rounded_rectangle([100, 700, 450, 780], radius=40, fill=COLOR_ACCENT_BLUE)
    draw.text((150, 715), datetime.now().strftime("%Y. %m. %d (%a)"), font=font_sub, fill=COLOR_TEXT_MAIN)
    
    img.save(os.path.join(OUTPUT_DIR, '01_cover.png'))

# 2. Market Mood
def create_mood():
    img, draw = create_base_image()
    draw_header_footer(draw, "Market Mood")
    
    # Split Layout
    # Fire (Up)
    draw.rectangle([50, 200, 520, 1100], fill=COLOR_CARD_BG)
    draw.text((180, 230), "🔥 급등", font=ImageFont.truetype(FONT_PATH, 50), fill=COLOR_ACCENT_RED)
    
    items_up = [("NVDA", "+12.5%"), ("AMD", "+8.2%"), ("TSLA", "+5.1%")]
    y = 350
    for ticker, change in items_up:
        draw.text((100, y), ticker, font=ImageFont.truetype(FONT_PATH, 60), fill=COLOR_TEXT_MAIN)
        draw.text((100, y+80), change, font=ImageFont.truetype(FONT_PATH, 50), fill=COLOR_ACCENT_RED)
        y += 200

    # Ice (Down)
    draw.rectangle([560, 200, 1030, 1100], fill=COLOR_CARD_BG)
    draw.text((690, 230), "❄️ 급락", font=ImageFont.truetype(FONT_PATH, 50), fill="#448AFF")
    
    items_down = [("INTC", "-15.2%"), ("AAPL", "-3.1%"), ("MSFT", "-2.5%")]
    y = 350
    for ticker, change in items_down:
        draw.text((610, y), ticker, font=ImageFont.truetype(FONT_PATH, 60), fill=COLOR_TEXT_MAIN)
        draw.text((610, y+80), change, font=ImageFont.truetype(FONT_PATH, 50), fill="#448AFF")
        y += 200

    img.save(os.path.join(OUTPUT_DIR, '02_mood.png'))

# 3. Tier Update
def create_tier():
    img, draw = create_base_image()
    draw_header_footer(draw, "Tier Updates")
    
    font_main = ImageFont.truetype(FONT_PATH, 60)
    font_desc = ImageFont.truetype(FONT_PATH, 40)
    
    # Card 1: New Tier 1
    draw.rounded_rectangle([50, 250, 1030, 550], radius=20, fill=COLOR_CARD_BG)
    draw.text((100, 300), "👑 NEW Tier 1 진입", font=font_main, fill=COLOR_TIER_GOLD)
    draw.text((100, 400), "AMD: AI 반도체 점유율 확대 기대감", font=font_desc, fill=COLOR_TEXT_MAIN)
    
    # Card 2: Rank Surge
    draw.rounded_rectangle([50, 600, 1030, 900], radius=20, fill=COLOR_CARD_BG)
    draw.text((100, 650), "🚀 순위 급상승", font=font_main, fill=COLOR_ACCENT_RED)
    draw.text((100, 750), "PLTR: (+45계단 상승)", font=font_desc, fill=COLOR_TEXT_MAIN)
    
    img.save(os.path.join(OUTPUT_DIR, '03_tier.png'))

# 4. Chart (Mock)
def create_chart():
    img, draw = create_base_image()
    draw_header_footer(draw, "Technical Signal")
    
    # Create matplotlib chart
    plt.figure(figsize=(8, 6), facecolor=COLOR_BG)
    plt.plot([1, 2, 3, 4, 5], [10, 12, 11, 15, 18], color=COLOR_ACCENT_GREEN, linewidth=3)
    plt.plot([1, 2, 3, 4, 5], [11, 11, 12, 13, 16], color='gray', linestyle='--', linewidth=2)
    plt.axis('off')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', facecolor=COLOR_BG)
    buf.seek(0)
    chart_img = Image.open(buf)
    
    # Paste chart
    img.paste(chart_img, (140, 300))
    
    draw.text((100, 250), "NVDA: MACD Golden Cross ✨", font=ImageFont.truetype(FONT_PATH, 60), fill=COLOR_ACCENT_GREEN)
    
    img.save(os.path.join(OUTPUT_DIR, '04_chart.png'))

# 5. Calendar
def create_calendar():
    img, draw = create_base_image()
    draw_header_footer(draw, "Key Events")
    
    font_day = ImageFont.truetype(FONT_PATH, 50)
    
    # Item 1
    draw.rounded_rectangle([50, 300, 1030, 500], radius=20, fill=COLOR_CARD_BG)
    draw.rounded_rectangle([80, 330, 200, 470], radius=10, fill=COLOR_ACCENT_RED)
    draw.text((100, 380), "D-Day", font=font_day, fill=COLOR_TEXT_MAIN)
    draw.text((250, 350), "TSLA 실적발표", font=font_day, fill=COLOR_TEXT_MAIN)
    draw.text((250, 420), "시장 예상 상회 가능성 ↑", font=ImageFont.truetype(FONT_PATH, 40), fill="#AAAAAA")

    # Item 2
    draw.rounded_rectangle([50, 550, 1030, 750], radius=20, fill=COLOR_CARD_BG)
    draw.rounded_rectangle([80, 580, 200, 720], radius=10, fill="#555555")
    draw.text((100, 630), "D-3", font=font_day, fill=COLOR_TEXT_MAIN)
    draw.text((250, 600), "KO 배당락일", font=font_day, fill=COLOR_TEXT_MAIN)
    draw.text((250, 670), "예상 배당수익률 3.1%", font=ImageFont.truetype(FONT_PATH, 40), fill="#AAAAAA")
    
    img.save(os.path.join(OUTPUT_DIR, '05_calendar.png'))

# 6. CTA
def create_cta():
    img, draw = create_base_image()
    
    font_cta = ImageFont.truetype(FONT_PATH, 70)
    draw.text((150, 500), "내 보유 종목은\n지금 안전할까?", font=font_cta, fill=COLOR_TEXT_MAIN, align="center")
    
    # Button
    draw.rounded_rectangle([200, 800, 880, 950], radius=75, fill=COLOR_ACCENT_BLUE)
    draw.text((320, 840), "Naspick 검색하기", font=font_cta, fill=COLOR_TEXT_MAIN)
    
    img.save(os.path.join(OUTPUT_DIR, '06_cta.png'))

if __name__ == "__main__":
    download_font()
    create_cover()
    create_mood()
    create_tier()
    create_chart()
    create_calendar()
    create_cta()
    print("✅ Images generated in temp_images/")
