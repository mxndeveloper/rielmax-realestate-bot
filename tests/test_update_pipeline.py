import pytest
from unittest.mock import patch, AsyncMock
from data.update_pipeline import update_listings_job
from database import init_db

@pytest.mark.asyncio
async def test_update_job():
    # Ensure database tables exist (including external_listings)
    await init_db()
    
    # Mock the fetcher to avoid real network calls (since proxies are dead)
    with patch('data.update_pipeline.CianListingFetcher') as MockFetcher:
        mock_instance = MockFetcher.return_value
        # Return a few fake listings to simulate success
        fake_listings = [
            {
                "external_id": "test_1",
                "source": "cian",
                "title": "Test Apartment",
                "description": "Nice place",
                "price": 10000000,
                "address": "Test St",
                "district": "Centre",
                "rooms": 2,
                "area_total": 55,
                "floor": 3,
                "floors_total": 10,
                "url": "https://cian.ru/test",
                "photos": [],
                "is_sponsored": False,
                "last_seen": "2024-01-01"
            }
        ]
        mock_instance.fetch_listings.return_value = fake_listings
        
        await update_listings_job()
        
        # Check that the external_listings table now has rows
        import aiosqlite
        from database import DB_PATH
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT COUNT(*) FROM external_listings") as cur:
                count = (await cur.fetchone())[0]
        assert count > 0