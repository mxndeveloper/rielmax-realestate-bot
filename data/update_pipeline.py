import asyncio
import pandas as pd
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from data.cian_parser import CianListingFetcher
from data.open_data_enricher import MoscowOpenDataEnricher
from database import save_listings_to_db
from config import FREE_PROXIES

async def update_listings_job():
    """Background job: fetch latest listings, enrich, store."""
    print("🔄 Running listing update job...")
    fetcher = CianListingFetcher(location="Москва", proxy_list=FREE_PROXIES)
    enricher = MoscowOpenDataEnricher()
    
    all_listings = []
    # Fetch for different room types (adjust as needed)
    for rooms in [1, 2, 3, None]:  # None = any rooms
        print(f"  Fetching {rooms if rooms else 'any'}-room listings...")
        listings = fetcher.fetch_listings(deal_type="sale", rooms=rooms, max_pages=2)
        all_listings.extend(listings)
        await asyncio.sleep(1)
    
    # Remove duplicates by external_id
    unique_dict = {}
    for lst in all_listings:
        ext_id = lst.get("external_id")
        if not ext_id:
            url = lst.get("url", "")
            ext_id = f"cian_{hash(url)}" if url else None
            if ext_id:
                lst["external_id"] = ext_id
        if ext_id and ext_id not in unique_dict:
            unique_dict[ext_id] = lst
    
    unique_listings = list(unique_dict.values())
    print(f"  Unique listings: {len(unique_listings)}")
    
    # Enrich with open data (mock for now)
    enriched = enricher.enrich_batch(unique_listings)
    
    # Save to database
    await save_listings_to_db(enriched)
    print(f"✅ Update complete. {len(enriched)} listings stored.")

def start_listing_updater():
    """Start the background scheduler (call this in main.py)."""
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        update_listings_job,
        trigger=IntervalTrigger(hours=6),
        id="listing_updater"
    )
    scheduler.start()
    print("📆 Listing updater scheduled every 6 hours.")