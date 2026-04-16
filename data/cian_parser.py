import requests
import json
import re
import random
import time
import pandas as pd
from typing import List, Dict, Any

class CianListingFetcher:
    def __init__(self, location="Москва", proxy_list=None):
        self.location = location
        self.proxy_list = proxy_list or []
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        })
        self.proxy_index = 0

    def _get_next_proxy(self):
        if not self.proxy_list:
            return None
        proxy = self.proxy_list[self.proxy_index]
        self.proxy_index = (self.proxy_index + 1) % len(self.proxy_list)
        return {"http": proxy, "https": proxy}

    def fetch_listings(self, deal_type="sale", rooms=None, max_pages=2) -> List[Dict[str, Any]]:
        all_listings = []
        for page in range(1, max_pages + 1):
            print(f"  Fetching CIAN page {page}...")
            url = "https://www.cian.ru/cat.php"
            params = {
                "deal_type": deal_type,
                "offer_type": "flat",
                "region": 1,  # Moscow
                "page": page,
            }
            if rooms:
                params["rooms"] = rooms

            # Try each proxy (or direct) until success
            for attempt in range(3):
                try:
                    proxies = self._get_next_proxy()
                    resp = self.session.get(url, params=params, proxies=proxies, timeout=20)
                    if resp.status_code == 200:
                        # Extract JSON data from the page
                        data = self._extract_json(resp.text)
                        if data and "offersSerialized" in data:
                            offers = json.loads(data["offersSerialized"])
                            for offer in offers:
                                listing = self._parse_offer(offer)
                                if listing:
                                    all_listings.append(listing)
                        break
                    else:
                        print(f"    HTTP {resp.status_code}, retrying...")
                except Exception as e:
                    print(f"    Attempt {attempt+1} failed: {e}")
                    time.sleep(2)
                    continue
            time.sleep(random.uniform(1, 3))
        return self._normalize_listings(all_listings)

    def _extract_json(self, html):
        """Extract the JSON data embedded in the page."""
        pattern = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
        match = re.search(pattern, html, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
                # Navigate to offers data
                return data.get("props", {}).get("pageProps", {}).get("initialState", {}).get("offersSerialized", {})
            except:
                return None
        return None

    def _parse_offer(self, offer):
        """Extract fields from a single offer JSON."""
        try:
            return {
                "external_id": str(offer.get("id")),
                "title": offer.get("title"),
                "description": offer.get("description"),
                "price": offer.get("bargainTerms", {}).get("price"),
                "address": offer.get("geo", {}).get("address"),
                "district": offer.get("geo", {}).get("district", {}).get("name"),
                "rooms": offer.get("roomsCount"),
                "area_total": offer.get("totalArea"),
                "floor": offer.get("floorNumber"),
                "floors_total": offer.get("building", {}).get("floorsCount"),
                "url": f"https://www.cian.ru/sale/flat/{offer.get('id')}/",
                "photos": [photo.get("fullUrl") for photo in offer.get("photos", [])],
            }
        except:
            return None

    def _normalize_listings(self, raw_listings):
        normalized = []
        for item in raw_listings:
            if not item:
                continue
            normalized.append({
                "external_id": item.get("external_id"),
                "source": "cian",
                "title": item.get("title"),
                "description": item.get("description", ""),
                "price": item.get("price"),
                "address": item.get("address"),
                "district": item.get("district"),
                "rooms": item.get("rooms"),
                "area_total": item.get("area_total"),
                "floor": item.get("floor"),
                "floors_total": item.get("floors_total"),
                "url": item.get("url"),
                "photos": item.get("photos", []),
                "is_sponsored": False,
                "last_seen": pd.Timestamp.now().isoformat()
            })
        return normalized