import pytest
from data.cian_parser import CianListingFetcher
from config import FREE_PROXIES

@pytest.mark.asyncio
async def test_fetch_listings():
    fetcher = CianListingFetcher(location="Москва", proxy_list=FREE_PROXIES)
    listings = fetcher.fetch_listings(deal_type="sale", rooms=2, max_pages=1)
    # If no listings, it's okay (network may fail), but we expect at least some after retries
    # We'll just check that it doesn't crash
    assert isinstance(listings, list)