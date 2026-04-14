import asyncio
import aiohttp
from bs4 import BeautifulSoup
import random

async def fetch_avito_listings():
    url = "https://www.avito.ru/moskva/kvartiry/prodam?q=2-комнатная+центр"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    proxy = "http://167.103.115.102:8800"
    # Wait a few seconds before request to avoid rate limiting
    await asyncio.sleep(random.uniform(2, 5))
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, proxy=proxy, headers=headers, timeout=15) as resp:
                if resp.status != 200:
                    print(f"HTTP {resp.status}")
                    return []
                html = await resp.text()
                soup = BeautifulSoup(html, "html.parser")
                items = soup.find_all("div", {"data-marker": "item"})[:5]
                results = []
                for item in items:
                    title_elem = item.find("h3", {"itemprop": "name"})
                    price_elem = item.find("span", {"itemprop": "price"})
                    title = title_elem.get_text(strip=True) if title_elem else "No title"
                    price = price_elem.get("content") if price_elem else "?"
                    results.append(f"{title} - {price} RUB")
                return results
        except Exception as e:
            print(f"Request error: {e}")
            return []

async def main():
    print("Fetching Avito listings...")
    listings = await fetch_avito_listings()
    if listings:
        print(f"Found {len(listings)} listings:")
        for i, lst in enumerate(listings, 1):
            print(f"{i}. {lst}")
    else:
        print("No listings or request failed")

asyncio.run(main())