import feedparser
import sys

def fetch_avito_rss(query="2-комнатная+центр"):
    url = f"https://www.avito.ru/moskva/kvartiry/prodam/rss?q={query}"
    print(f"Fetching: {url}")
    feed = feedparser.parse(url)
    if feed.bozo:  # if parsing error
        print(f"Feed parsing error: {feed.bozo_exception}")
    print(f"Feed entries count: {len(feed.entries)}")
    results = []
    for entry in feed.entries[:5]:
        # Try to extract price from title or summary if not directly available
        price = entry.get("price")
        if not price:
            # Sometimes price is in the title like "2-к. квартира, 55 м², 15 000 000 ₽"
            import re
            match = re.search(r'(\d[\d\s]+)₽', entry.title)
            if match:
                price = match.group(1).strip()
        results.append({
            "title": entry.title,
            "link": entry.link,
            "price": price or "?",
            "description": entry.get("summary", "")[:100],
        })
    return results

def fetch_cian_rss():
    # CIAN RSS for Moscow flats for sale
    url = "https://www.cian.ru/cat.php?currency=rub&deal_type=sale&engine_version=2&offer_type=flat&region=1&rss=1"
    print(f"Fetching: {url}")
    feed = feedparser.parse(url)
    if feed.bozo:
        print(f"Feed parsing error: {feed.bozo_exception}")
    print(f"Feed entries count: {len(feed.entries)}")
    results = []
    for entry in feed.entries[:5]:
        results.append({
            "title": entry.title,
            "link": entry.link,
            "price": entry.get("price", "?"),
            "description": entry.get("summary", "")[:100],
        })
    return results

if __name__ == "__main__":
    print("Avito RSS:")
    for item in fetch_avito_rss():
        print(f"{item['title']} - {item['price']} RUB")
    print("\nCIAN RSS:")
    for item in fetch_cian_rss():
        print(f"{item['title']} - {item['price']} RUB")