
import os
import requests
import json
import time

# Configuration
# ==============================================================================
# GitHub Actions에서는 Secrets의 환경변수를 사용하고, 로컬에서는 아래 하드코딩된 값을 사용합니다.
# 1. 텔레그램 봇 토큰
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8447711529:AAE7xlmbkAc-QWblJPDSsU0ETJV5ek63-L8') 

# 2. 채널/채팅방 ID
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '-1003880671265')

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMediaGroup"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')

def send_daily_briefing():
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Error: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not found in environment variables.")
        return

    print("🚀 Sending Daily Briefing to Telegram...")

    # Get sorted list of images
    # Sort ensures 01_cover, 02_tier, 02_tier_2, ... are in order
    files = sorted([f for f in os.listdir(OUTPUT_DIR) if f.endswith('.png')])
    
    if not files:
        print("❌ No images found to send.")
        return

    print(f"📸 Found {len(files)} images to send.")

    # Telegram sendMediaGroup limit is 10 items. 
    # If we have more, we need to chunk them.
    def chunk_list(lst, n):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    chunks = list(chunk_list(files, 10))
    
    for chunk_idx, chunk_files in enumerate(chunks):
        media = []
        files_to_close = []
        files_data = {}
        
        try:
            for i, filename in enumerate(chunk_files):
                file_path = os.path.join(OUTPUT_DIR, filename)
                f_obj = open(file_path, 'rb')
                files_to_close.append(f_obj)
                
                media_item = {
                    'type': 'photo',
                    'media': f'attach://{filename}'
                }
                
                # Add caption ONLY to the very first image of the first chunk
                if chunk_idx == 0 and i == 0:
                    from datetime import datetime
                    date_str = datetime.now().strftime("%Y-%m-%d")
                    media_item['caption'] = f"📊 **NASPICK Daily Briefing** ({date_str})\n\n🇺🇸 미국주식 시장의 핵심 흐름을 1분 만에 확인하세요.\n\n👉 전체 랭킹 확인: https://naspick.com"
                    media_item['parse_mode'] = 'Markdown'
                
                media.append(media_item)
                files_data[filename] = f_obj

            payload = {
                'chat_id': CHAT_ID,
                'media': json.dumps(media)
            }

            print(f"📤 Sending Chunk {chunk_idx+1}/{len(chunks)} ({len(chunk_files)} images)...")
            response = requests.post(API_URL, data=payload, files=files_data)
            
            if response.status_code == 200:
                print(f"✅ Chunk {chunk_idx+1} sent successfully.")
            else:
                print(f"❌ Failed to send chunk {chunk_idx+1}: {response.text}")
            
            # Rate limit politeness
            time.sleep(1) 

        except Exception as e:
            print(f"❌ Error sending chunk {chunk_idx+1}: {e}")
        finally:
            for f in files_to_close:
                f.close()

if __name__ == "__main__":
    send_daily_briefing()
