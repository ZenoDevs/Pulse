"""
CLI tool per testare gli scrapers
"""
import argparse
from datetime import datetime, timedelta
from scrapers import scraper_registry


def main():
    parser = argparse.ArgumentParser(description='Test Pulse scrapers')
    parser.add_argument('query', help='Search query')
    parser.add_argument(
        '--sources',
        nargs='+',
        help='Sources to scrape (default: all)',
        default=None
    )
    parser.add_argument('--max-pages', type=int, default=5, help='Max pages per source')
    parser.add_argument('--days-back', type=int, default=7, help='Days to look back')
    parser.add_argument('--output', help='Output CSV file')
    
    args = parser.parse_args()
    
    # Date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=args.days_back)
    
    print(f"\n🔍 Scraping per: '{args.query}'")
    print(f"📅 Range: {start_date.date()} -> {end_date.date()}")
    print(f"📰 Fonti: {args.sources or 'tutte'}\n")
    
    # Scraping
    df = scraper_registry.scrape_all(
        query=args.query,
        sources=args.sources,
        max_pages=args.max_pages,
        start_date=start_date,
        end_date=end_date
    )
    
    if df.empty:
        print("\n❌ Nessun risultato trovato")
        return
    
    # Mostra risultati
    print(f"\n✅ Trovati {len(df)} articoli:")
    print(f"   - Fonti: {df['source'].value_counts().to_dict()}")
    print(f"   - Range date: {df['published_at'].min()} -> {df['published_at'].max()}")
    
    # Mostra sample
    print("\n📄 Sample articoli:")
    for idx, row in df.head(3).iterrows():
        print(f"\n  [{row['source']}] {row['title']}")
        print(f"  {row['published_at']}")
        print(f"  {row['content'][:100]}...")
    
    # Salva se richiesto
    if args.output:
        df.to_csv(args.output, index=False)
        print(f"\n💾 Salvato in: {args.output}")


if __name__ == "__main__":
    main()
