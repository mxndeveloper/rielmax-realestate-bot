import pytest
from database import UserDB, ListingDB, AlertDB

@pytest.mark.asyncio
async def test_set_and_get_role(db):
    await UserDB.set_role(123, "Риелтор")
    role = await UserDB.get_role(123)
    assert role == "Риелтор"

@pytest.mark.asyncio
async def test_set_and_get_language(db):
    await UserDB.set_language(123, "en")
    lang = await UserDB.get_language(123)
    assert lang == "en"

@pytest.mark.asyncio
async def test_set_and_get_premium(db):
    await UserDB.set_premium(123, True)
    assert await UserDB.is_premium(123) is True

@pytest.mark.asyncio
async def test_add_and_get_listing(db):
    listing_id = await ListingDB.add_listing(
        user_id=123,
        title="Test",
        description="Desc",
        price=10000000,
        district="Centre",
        address="Test St",
        photos="[]"
    )
    listings = await ListingDB.get_user_listings(123)
    assert len(listings) == 1
    assert listings[0]["title"] == "Test"

@pytest.mark.asyncio
async def test_add_and_get_alert(db):
    alert_id = await AlertDB.add_alert(123, "Centre", 15000000)
    alerts = await AlertDB.get_user_alerts(123)
    assert len(alerts) == 1
    assert alerts[0]["max_price"] == 15000000