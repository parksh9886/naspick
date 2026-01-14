import requests
import time

# Candidate: Second half of the user provided string
KEY_TO_TEST = "d5joti1r01qjaedqu46g" 

FINNHUB_BASE_URL = "https://finnhub.io/api/v1"

def fetch_consensus_data(ticker, key):
    print(f"Testing Key: {key}")
    try:
        # A. Price Target
        target_url = f"{FINNHUB_BASE_URL}/stock/price-target?symbol={ticker}&token={key}"
        r_target = requests.get(target_url)
        target_data = r_target.json()
        
        if 'error' in target_data:
            print(f"❌ Target Error: {target_data}")
        elif 'targetMean' in target_data:
            print(f"✅ Target Success used key ending in ...{key[-3:]}: ${target_data['targetMean']}")
        else:
            print(f"⚠️ Target Empty/Unknown: {target_data}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_consensus_data("AAPL", KEY_TO_TEST)


