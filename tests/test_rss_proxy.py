import requests
import feedparser

proxy = "http://167.103.115.102:8800"
proxies = {"http": proxy, "https": proxy}
url = "https://www.avito.ru/moskva/kvartiry/prodam/rss?q=2-комнатная+центр"
try:
    resp = requests.get(url, proxies=proxies, timeout=15)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        feed = feedparser.parse(resp.text)
        print(f"Entries: {len(feed.entries)}")
        for entry in feed.entries[:3]:
            print(entry.title)
    else:
        print("Failed")
except Exception as e:
    print(f"Error: {e}")