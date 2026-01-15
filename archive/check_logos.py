import urllib.request
import urllib.error

def check_url(url):
    try:
        urllib.request.urlopen(url)
        return "OK"
    except urllib.error.HTTPError as e:
        return f"Error {e.code}"
    except Exception as e:
        return f"Error {e}"

urls = [
    "https://financialmodelingprep.com/image-stock/AAPL.png",
    "https://financialmodelingprep.com/image-stock/BRK.B.png",
    "https://financialmodelingprep.com/image-stock/BRK-B.png",
    "https://financialmodelingprep.com/image-stock/BF.B.png",
    "https://financialmodelingprep.com/image-stock/BF-B.png"
]

for url in urls:
    print(f"{url}: {check_url(url)}")
