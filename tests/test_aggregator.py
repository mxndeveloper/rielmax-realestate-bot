#!/usr/bin/env python3
"""
Test script for external listing aggregators.
Run this script to verify that each adapter can fetch real listings.
Usage: python test_aggregator.py [--source cian|avito|yandex|domofond] [--limit 5]
"""

import asyncio
import argparse
import sys
from typing import List, Dict, Any

# Add project root to path
sys.path.insert(0, '.')

# Import adapters (they may have missing dependencies – we'll handle gracefully)
try:
    from aggregator.cian_adapter import CianAdapter
except ImportError:
    CianAdapter = None
try:
    from aggregator.avito_adapter import AvitoAdapter
except ImportError:
    AvitoAdapter = None
try:
    from aggregator.yandex_adapter import YandexAdapter
except ImportError:
    YandexAdapter = None
try:
    from aggregator.domofond_adapter import DomofondAdapter
except ImportError:
    DomofondAdapter = None

# Shared proxy list (same as in main.py)
FREE_PROXIES = [
    "http://167.103.115.102:8800",
    "http://5.250.183.76:3128",
    "http://14.97.89.207:80",
    "http://167.71.5.83:8080",
    "http://192.241.132.32:3128",
    "http://8.213.151.128:3128",
    "http://195.26.224.135:80",
    "http://167.99.236.14:80",
    "http://38.34.179.179:8449",
    "http://41.220.16.218:80",
    "http://111.79.111.126:3128",
    "http://173.245.49.222:80",
    "http://173.245.49.105:80",
    "http://173.245.49.112:80",
    "http://173.245.49.163:80",
]

async def test_adapter(adapter_class, name: str, limit: int = 5, query: str = "Москва"):
    """Test a single adapter and print results."""
    if adapter_class is None:
        print(f"❌ {name} adapter not available (missing dependencies)")
        return

    print(f"\n🔍 Testing {name} adapter...")
    try:
        # For Avito, pass proxy list
        if name.lower() == "avito":
            adapter = adapter_class(proxy_list=FREE_PROXIES)
        else:
            adapter = adapter_class()

        # Fetch listings
        listings = await adapter.fetch(query=query, limit=limit)

        if not listings:
            print(f"⚠️ {name} returned 0 listings (maybe blocked or no results)")
        else:
            print(f"✅ {name} fetched {len(listings)} listings")
            for i, listing in enumerate(listings[:3], 1):
                print(f"  {i}. {listing.get('title', 'No title')[:60]} - {listing.get('price', '?')} ₽")
            if len(listings) > 3:
                print(f"  ... and {len(listings)-3} more")

        # Test sponsored (if implemented)
        sponsored = await adapter.get_sponsored()
        if sponsored:
            print(f"⭐ {name} has {len(sponsored)} sponsored listings")
    except Exception as e:
        print(f"❌ {name} error: {e}")

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=["cian", "avito", "yandex", "domofond"], help="Test only one source")
    parser.add_argument("--limit", type=int, default=5, help="Number of listings to fetch per source")
    parser.add_argument("--query", default="2-комнатная квартира Москва центр", help="Search query")
    args = parser.parse_args()

    adapters = []
    if not args.source or args.source == "cian":
        adapters.append((CianAdapter, "CIAN"))
    if not args.source or args.source == "avito":
        adapters.append((AvitoAdapter, "Avito"))
    if not args.source or args.source == "yandex":
        adapters.append((YandexAdapter, "Yandex"))
    if not args.source or args.source == "domofond":
        adapters.append((DomofondAdapter, "Domofond"))

    print(f"Testing aggregators with query: {args.query}\nLimit per source: {args.limit}\n")
    for adapter_class, name in adapters:
        await test_adapter(adapter_class, name, args.limit, args.query)

if __name__ == "__main__":
    asyncio.run(main())