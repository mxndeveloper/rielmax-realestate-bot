import feedparser
import requests

# Try without proxy first
url = "https://www.cian.ru/cat.php?currency=rub&deal_type=sale&engine_version=2&offer_type=flat&region=1&rss=1"
resp = requests.get(url, timeout=10)
if resp.status_code == 200:
    feed = feedparser.parse(resp.text)
    print(f"Entries: {len(feed.entries)}")
    for entry in feed.entries[:3]:
        print(entry.title)
else:
    print(f"HTTP {resp.status_code}, trying with proxy...")
    proxy = {"http": "http://167.103.115.102:8800", "https": "http://167.103.115.102:8800"}
    resp = requests.get(url, proxies=proxy, timeout=10)
    if resp.status_code == 200:
        feed = feedparser.parse(resp.text)
        print(f"Entries with proxy: {len(feed.entries)}")
        for entry in feed.entries[:3]:
            print(entry.title)
    else:
        print("Both attempts failed.")