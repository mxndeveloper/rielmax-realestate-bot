from data.open_data_enricher import MoscowOpenDataEnricher

def test_enrich():
    enricher = MoscowOpenDataEnricher()
    sample = {"address": "ул. Тверская, 1"}
    enriched = enricher.enrich_listing(sample)
    assert "official_address" in enriched