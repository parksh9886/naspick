# stock_names.py

# Mapping of Ticker -> { "kr": "Korean Name", "en": "English Name" }
# This covers major S&P 500 and Nasdaq 100 stocks.

STOCK_NAMES = {
    "AAPL": {"kr": "애플", "en": "Apple Inc."},
    "MSFT": {"kr": "마이크로소프트", "en": "Microsoft"},
    "NVDA": {"kr": "엔비디아", "en": "NVIDIA"},
    "GOOGL": {"kr": "알파벳 A", "en": "Alphabet A"},
    "GOOG": {"kr": "알파벳 C", "en": "Alphabet C"},
    "AMZN": {"kr": "아마존", "en": "Amazon"},
    "META": {"kr": "메타", "en": "Meta Platforms"},
    "TSLA": {"kr": "테슬라", "en": "Tesla"},
    "AVGO": {"kr": "브로드컴", "en": "Broadcom"},
    "AMD": {"kr": "AMD", "en": "Advanced Micro Devices"},
    "NFLX": {"kr": "넷플릭스", "en": "Netflix"},
    "INTC": {"kr": "인텔", "en": "Intel"},
    "QCOM": {"kr": "퀄컴", "en": "Qualcomm"},
    "PEP": {"kr": "펩시코", "en": "PepsiCo"},
    "COST": {"kr": "코스트코", "en": "Costco"},
    "CSCO": {"kr": "시스코", "en": "Cisco"},
    "TMUS": {"kr": "티모바일", "en": "T-Mobile"},
    "CMCSA": {"kr": "컴캐스트", "en": "Comcast"},
    "TXN": {"kr": "텍사스 인스트루먼트", "en": "Texas Instruments"},
    "ADBE": {"kr": "어도비", "en": "Adobe"},
    "AMGN": {"kr": "암젠", "en": "Amgen"},
    "HON": {"kr": "허니웰", "en": "Honeywell"},
    "SBUX": {"kr": "스타벅스", "en": "Starbucks"},
    "MDLZ": {"kr": "몬델리즈", "en": "Mondelez"},
    "GILD": {"kr": "길리어드", "en": "Gilead Sciences"},
    "ISRG": {"kr": "인튜이티브 서지컬", "en": "Intuitive Surgical"},
    "VRTX": {"kr": "버텍스", "en": "Vertex Pharma"},
    "REGN": {"kr": "리제네론", "en": "Regeneron"},
    "ADP": {"kr": "ADP", "en": "Automatic Data Processing"},
    "BKNG": {"kr": "부킹 홀딩스", "en": "Booking Holdings"},
    "JNJ": {"kr": "존슨앤존슨", "en": "Johnson & Johnson"},
    "JPM": {"kr": "제이피모건", "en": "JPMorgan Chase"},
    "PG": {"kr": "P&G", "en": "Procter & Gamble"},
    "V": {"kr": "비자", "en": "Visa"},
    "MA": {"kr": "마스터카드", "en": "Mastercard"},
    "HD": {"kr": "홈디포", "en": "Home Depot"},
    "CVX": {"kr": "쉐브론", "en": "Chevron"},
    "MRK": {"kr": "머크", "en": "Merck"},
    "ABBV": {"kr": "애브비", "en": "AbbVie"},
    "KO": {"kr": "코카콜라", "en": "Coca-Cola"},
    "BAC": {"kr": "뱅크오브아메리카", "en": "Bank of America"},
    "PFE": {"kr": "화이자", "en": "Pfizer"},
    "TMO": {"kr": "써모피셔", "en": "Thermo Fisher"},
    "WMT": {"kr": "월마트", "en": "Walmart"},
    "DIS": {"kr": "월트 디즈니", "en": "Disney"},
    "ACN": {"kr": "엑센츄어", "en": "Accenture"},
    "ABT": {"kr": "애보트", "en": "Abbott"},
    "DHR": {"kr": "다나허", "en": "Danaher"},
    "LIN": {"kr": "린데", "en": "Linde"},
    "NKE": {"kr": "나이키", "en": "Nike"},
    "VZ": {"kr": "버라이즌", "en": "Verizon"},
    "ORCL": {"kr": "오라클", "en": "Oracle"}
}

def get_name(ticker):
    """Returns {name: DisplayName(KR prefer), name_en: EnglishName}"""
    if ticker in STOCK_NAMES:
        return {
            "name": STOCK_NAMES[ticker]["kr"], # Use Korean as primary display
            "name_en": STOCK_NAMES[ticker]["en"]
        }
    return {
        "name": ticker,
        "name_en": ticker
    }
