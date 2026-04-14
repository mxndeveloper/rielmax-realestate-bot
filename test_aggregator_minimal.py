import asyncio
import sys
sys.path.insert(0, '.')

from aggregator.cian_adapter import CianAdapter
from aggregator.avito_adapter import AvitoAdapter

async def test():
    print("Testing CIAN...")
    cian = CianAdapter()
    try:
        listings = await cian.fetch(limit=2)
        print(f"CIAN got {len(listings)} listings")
        for l in listings:
            print(l.get('title', '?')[:60])
    except Exception as e:
        print(f"CIAN error: {e}")

    print("
Testing Avito...")
    avito = AvitoAdapter(proxy_list=["http://167.103.115.102:8800"])
    try:
        listings = await avito.fetch(limit=2)
        print(f"Avito got {len(listings)} listings")
        for l in listings:
            print(l.get('title', '?')[:60])
    except Exception as e:
        print(f"Avito error: {e}")

asyncio.run(test())
