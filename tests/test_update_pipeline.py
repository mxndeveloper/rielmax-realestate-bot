import pytest
from data.update_pipeline import update_listings_job
import asyncio

@pytest.mark.asyncio
async def test_update_job():
    # This will actually fetch real data – run only occasionally
    await update_listings_job()
    # Check if database was populated
    import aiosqlite
    from database import DB_PATH
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM external_listings") as cur:
            count = (await cur.fetchone())[0]
    assert count > 0