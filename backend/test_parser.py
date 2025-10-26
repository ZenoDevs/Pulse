"""
Test script for Parser Service
"""
import sys
from datetime import datetime, timedelta
sys.path.append('/Users/Edoardo.dng/Desktop/Pulse/Pulse/backend')

from scrapers import scraper_registry
from services.parser_service import parser_service


def test_parser_with_real_data():
    """Test parser with real scraped data"""
    
    print("=" * 60)
    print("TESTING PARSER SERVICE WITH REAL DATA")
    print("=" * 60)
    
    # 1. Scrape real data
    print("\n1️⃣  Scraping real articles from ANSA...")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    df = scraper_registry.scrape_all(
        query="intelligenza artificiale",
        sources=['ansa'],
        max_pages=2,
        start_date=start_date,
        end_date=end_date
    )
    
    if df.empty:
        print("❌ No articles found!")
        return
    
    print(f"✅ Scraped {len(df)} raw articles\n")
    
    # 2. Parse articles
    print("2️⃣  Parsing and normalizing articles...")
    
    parsed_articles = parser_service.parse_dataframe(df, 'ansa')
    
    print(f"✅ Parsed {len(parsed_articles)} articles\n")
    
    # 3. Show sample
    print("3️⃣  Sample parsed article:")
    print("-" * 60)
    
    if parsed_articles:
        sample = parsed_articles[0]
        print(f"Source: {sample.source}")
        print(f"Source ID: {sample.source_id}")
        print(f"Title: {sample.title[:80]}...")
        print(f"Content: {sample.content[:150]}...")
        print(f"URL: {sample.url}")
        print(f"Published: {sample.published_at}")
        print(f"Metadata: {sample.raw_metadata}")
    
    print("\n" + "-" * 60)
    
    # 4. Test deduplication
    print("\n4️⃣  Testing deduplication...")
    
    # Create some duplicates by adding same article twice
    test_articles = parsed_articles[:3] + parsed_articles[:2]
    print(f"Articles before dedup: {len(test_articles)}")
    
    unique_articles = parser_service.deduplicate_articles(
        test_articles,
        similarity_threshold=0.85
    )
    
    print(f"Articles after dedup: {len(unique_articles)}")
    print(f"✅ Removed {len(test_articles) - len(unique_articles)} duplicates\n")
    
    # 5. Test HTML cleaning
    print("5️⃣  Testing HTML cleaning...")
    
    dirty_text = "<p>Test <b>bold</b> and <script>alert('xss')</script> text</p>"
    clean_text = parser_service.clean_html(dirty_text)
    print(f"Dirty: {dirty_text}")
    print(f"Clean: {clean_text}")
    print(f"✅ HTML cleaned\n")
    
    # 6. Test date normalization
    print("6️⃣  Testing date normalization...")
    
    test_dates = [
        "2024-12-25 10:30:00",
        "25.12.2024, 10:30",
        datetime.now(),
        None
    ]
    
    for test_date in test_dates:
        normalized = parser_service.normalize_date(test_date)
        print(f"Input: {test_date}")
        print(f"Output: {normalized}")
        print()
    
    print("=" * 60)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    test_parser_with_real_data()
