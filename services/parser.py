import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict
import random
import asyncio

async def search_external_listings(query: str, limit: int = 12) -> List[Dict]:
    """
    Advanced async scraper for Avito.ru and Cian.ru
    Returns structured data ready for search results + sponsored logic
    """
    results = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    q = query.replace(" ", "+")

    # === Avito Search ===
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            url = f"https://www.avito.ru/all/nedvizhimost?q={q}"
            async with session.get(url, timeout=15) as resp:
                if resp.status == 200:
                    soup = BeautifulSoup(await resp.text(), "html.parser")
                    items = soup.find_all("div", {"data-marker": "item"})[:limit]

                    for item in items:
                        try:
                            title = item.find("h3").get_text(strip=True)
                            price_tag = item.find("span", string=lambda x: x and "₽" in str(x))
                            price = int("".join(filter(str.isdigit, price_tag.get_text()))) if price_tag else 0
                            link = "https://avito.ru" + item.find("a")["href"] if item.find("a") else "#"

                            results.append({
                                "title": title,
                                "price": price,
                                "district": "Avito",
                                "description": "Актуальное объявление с Avito",
                                "source": "avito",
                                "url": link,
                                "is_sponsored": False
                            })
                        except:
                            continue
    except Exception as e:
        print(f"Avito scrape error: {e}")

    # === Cian Search ===
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            url = f"https://www.cian.ru/cat.php?query={q}"
            async with session.get(url, timeout=15) as resp:
                if resp.status == 200:
                    soup = BeautifulSoup(await resp.text(), "html.parser")
                    items = soup.find_all("article", {"data-name": "CardComponent"})[:limit]

                    for item in items:
                        try:
                            title = item.find("span", {"data-name": "Title"}).get_text(strip=True)
                            price_tag = item.find("span", {"data-name": "Price"})
                            price = int("".join(filter(str.isdigit, price_tag.get_text()))) if price_tag else 0

                            results.append({
                                "title": title,
                                "price": price,
                                "district": "ЦИАН",
                                "description": "Актуальное объявление с Cian.ru",
                                "source": "cian",
                                "url": "#",
                                "is_sponsored": False
                            })
                        except:
                            continue
    except Exception as e:
        print(f"Cian scrape error: {e}")

    # Shuffle to avoid always showing same results
    random.shuffle(results)
    return results[:limit]