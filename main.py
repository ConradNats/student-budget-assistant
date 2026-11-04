#!/usr/bin/env python3
"""Main entry point for Jumia Uganda Price Tracker."""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from jumia_tracker import JumiaCloudScraper, JumiaCookieScraper, JumiaDatabase, JumiaScraper, JumiaSeleniumScraper, analyze_prices


def scrape(args):
    """Run scraper."""
    max_pages = args.max_pages if args.max_pages >= 0 else None
    use_selenium = getattr(args, 'selenium', False)
    use_cookies = getattr(args, 'cookies', False)
    use_cloud = getattr(args, 'cloudscraper', False) and not use_selenium and not use_cookies
    
    if use_cookies:
        print("Starting Cookie-based scraper...")
        scraper = JumiaCookieScraper(cookies_file=getattr(args, 'cookies_file', 'cookies.json'), save_to_db=not args.no_db)
    elif use_selenium:
        print("Starting Selenium scraper (handles anti-bot protection)...")
        scraper = JumiaSeleniumScraper(save_to_db=not args.no_db, headless=not getattr(args, 'no_headless', False))
    elif use_cloud:
        print("Starting CloudScraper (bypasses Cloudflare)...")
        try:
            scraper = JumiaCloudScraper(save_to_db=not args.no_db)
        except Exception as e:
            print(f"CloudScraper failed: {e}")
            print("Falling back to Selenium...")
            scraper = JumiaSeleniumScraper(save_to_db=not args.no_db, headless=not getattr(args, 'no_headless', False))
    else:
        print("Starting requests scraper...")
        scraper = JumiaScraper(save_to_db=not args.no_db)
    
    print(f"Max pages per category: {max_pages or 'all'}")
    print(f"Saving to: CSV, JSON, and {'SQLite DB' if not args.no_db else 'NO DB'}")
    try:
        df = scraper.scrape_all_categories(max_pages_per_category=max_pages)
        print(f"\nScraped {len(df)} products total")
    finally:
        scraper.close()


def analyze(args):
    """Run analysis."""
    csv_file = args.csv or 'data/raw/test_price_history.csv'
    product_name = args.product or 'Product'
    print(f"Analyzing {csv_file}...")
    analyze_prices(csv_file, product_name, save_path=args.output or 'price_history_chart.png')


def generate_test(args):
    """Generate test data."""
    import subprocess
    subprocess.run([sys.executable, 'scripts/generate_test_data.py'])


def export_db(args):
    """Export from database."""
    db = JumiaDatabase()
    days = args.days if args.days and args.days > 0 else None
    if args.format in ['csv', 'both']:
        db.export_to_csv(days=days)
    if args.format in ['json', 'both']:
        db.export_to_json(days=days)
    db.get_stats()
    db.close()


def db_stats(args):
    """Show database statistics."""
    db = JumiaDatabase()
    db.get_stats()
    db.close()


def main():
    parser = argparse.ArgumentParser(
        description="Jumia Uganda Price Tracker - Scrape and analyze prices over time",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py scrape --max-pages 1              # Test scrape
  python main.py scrape --cookies --max-pages 1   # Use saved cookies (if Cloudflare blocks)
  python main.py scrape --selenium --max-pages 1  # Use Selenium
  python main.py scrape                            # Scrape all pages for today
  python main.py scrape --max-pages 2             # Scrape 2 pages per category
  python main.py scrape --no-db                   # Scrape without saving to database
  python main.py analyze --csv data/raw/jumia_prices_20251028_123045.csv
  python main.py generate-test                    # Generate test price data
  python main.py export --format both --days 7   # Export last 7 days from DB
  python main.py db-stats                         # View database statistics
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Scrape Jumia products (saves to CSV, JSON & DB)')
    scrape_parser.add_argument('--max-pages', type=int, default=1, 
                               help='Max pages per category (default: 1 for testing, use -1 for all)')
    scrape_parser.add_argument('--no-db', action='store_true',
                               help='Do not save to SQLite database')
    scrape_parser.add_argument('--selenium', action='store_true',
                               help='Use Selenium browser (for sites with anti-bot protection)')
    scrape_parser.add_argument('--cloudscraper', action='store_true',
                               help='Use CloudScraper (bypasses Cloudflare)')
    scrape_parser.add_argument('--cookies', action='store_true',
                               help='Use saved cookies from cookies.json')
    scrape_parser.add_argument('--cookies-file', default='cookies.json',
                               help='Path to cookies JSON file')
    scrape_parser.add_argument('--no-headless', action='store_true',
                               help='Show browser window when using Selenium')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze price history')
    analyze_parser.add_argument('--csv', help='Path to CSV file')
    analyze_parser.add_argument('--product', help='Product name')
    analyze_parser.add_argument('--output', help='Output chart filename')
    
    # Generate test data
    subparsers.add_parser('generate-test', help='Generate test price data')
    
    # Export from database
    export_parser = subparsers.add_parser('export', help='Export data from database')
    export_parser.add_argument('--format', choices=['csv', 'json', 'both'], default='both',
                               help='Export format (default: both)')
    export_parser.add_argument('--days', type=int, help='Number of days to export (default: all)')
    
    # Database stats
    subparsers.add_parser('db-stats', help='Show database statistics')
    
    args = parser.parse_args()
    
    if args.command == 'scrape':
        scrape(args)
    elif args.command == 'analyze':
        analyze(args)
    elif args.command == 'generate-test':
        generate_test(args)
    elif args.command == 'export':
        export_db(args)
    elif args.command == 'db-stats':
        db_stats(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
