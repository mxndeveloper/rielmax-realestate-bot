import pytest
from data.cian_parser import CianListingFetcher

@pytest.mark.asyncio
async def test_fetch_listings():
    fetcher = CianListingFetcher(location="Москва")
    listings = fetcher.fetch_listings(deal_type="sale", rooms=2, max_pages=1)
    assert len(listings) > 0
    assert "title" in listings[0]
    assert "price" in listings[0]
    print(f"Sample: {listings[0]['title']}")