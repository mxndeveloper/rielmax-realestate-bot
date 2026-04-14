import asyncio
import sys
sys.path.insert(0, '.')

try:
    from aggregator.cian_adapter import CianAdapter
    print("CIAN adapter loaded")
except Exception as e:
    print(f"CIAN error: {e}")

try:
    from aggregator.avito_adapter import AvitoAdapter
    print("Avito adapter loaded")
except Exception as e:
    print(f"Avito error: {e}")

async def test():
    if CianAdapter:
        print("\nTesting CIAN...")
        adapter = CianAdapter()
        try:
            listings = await adapter.fetch(limit=2)
            print(f"Got {len(listings)} listings")
            for l in listings:
                print(l.get('title', '')[:50])
        except Exception as e:
            print(f"CIAN fetch error: {e}")
    if AvitoAdapter:
        print("\nTesting Avito...")
        adapter = AvitoAdapter(proxy_list=["http://167.103.115.102:8800"])
        try:
            listings = await adapter.fetch(limit=2)
            print(f"Got {len(listings)} listings")
            for l in listings:
                print(l.get('title', '')[:50])
        except Exception as e:
            print(f"Avito fetch error: {e}")

asyncio.run(test())
