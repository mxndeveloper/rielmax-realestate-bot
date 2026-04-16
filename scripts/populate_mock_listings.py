import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from database import init_db, save_listings_to_db

MOCK_LISTINGS = [
    {
        "external_id": "mock_1",
        "source": "mock",
        "title": "2-комнатная квартира в центре Москвы",
        "description": "Просторная квартира с евроремонтом, 5 мин от метро",
        "price": 15000000,
        "address": "ул. Тверская, 10",
        "district": "Центральный",
        "rooms": 2,
        "area_total": 55.5,
        "floor": 5,
        "floors_total": 12,
        "url": "https://example.com/mock1",
        "photos": "",
        "is_sponsored": False,
        "last_seen": "2026-04-16T12:00:00"
    },
    {
        "external_id": "mock_2",
        "source": "mock",
        "title": "3-комнатная квартира в Хамовниках",
        "description": "Элитная квартира рядом с парком",
        "price": 25000000,
        "address": "ул. Пречистенка, 5",
        "district": "Хамовники",
        "rooms": 3,
        "area_total": 85.0,
        "floor": 8,
        "floors_total": 10,
        "url": "https://example.com/mock2",
        "photos": "",
        "is_sponsored": True,
        "last_seen": "2026-04-16T12:00:00"
    },
    {
        "external_id": "mock_3",
        "source": "mock",
        "title": "Студия в ММДЦ Москва-Сити",
        "description": "Вид на город, отделка премиум-класса",
        "price": 12000000,
        "address": "Пресненская наб., 2",
        "district": "Пресненский",
        "rooms": 1,
        "area_total": 38.0,
        "floor": 25,
        "floors_total": 70,
        "url": "https://example.com/mock3",
        "photos": "",
        "is_sponsored": False,
        "last_seen": "2026-04-16T12:00:00"
    }
]

async def main():
    await init_db()
    await save_listings_to_db(MOCK_LISTINGS)
    print(f"✅ Added {len(MOCK_LISTINGS)} mock listings to external_listings.")

if __name__ == "__main__":
    asyncio.run(main())