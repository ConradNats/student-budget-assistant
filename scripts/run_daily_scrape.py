#!/usr/bin/env python3
"""Daily scraper script for continuous price tracking over weeks."""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

try:
    from jumia_tracker import JumiaScraper
except ImportError:
    try:
        from JumiaTracker import JumiaScraper
    except ImportError:
        raise


def main():
    """Run daily scrape with full tracking."""
    print(f"=== Daily Jumia Price Scrape - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    
    scraper = JumiaScraper(save_to_db=True)
    
    max_pages = int(os.environ.get('MAX_PAGES_PER_CATEGORY', '3'))
    
    print(f"Scraping up to {max_pages} pages per category")
    print("Files will be saved as CSV and JSON with timestamps")
    print("Data will be stored in SQLite database for long-term tracking\n")
    
    try:
        df = scraper.scrape_all_categories(max_pages_per_category=max_pages)
        print(f"\n✅ Successfully scraped {len(df)} products")
        print("📁 Check data/raw/ for CSV and JSON files")
        print("💾 Check data/processed/jumia_tracker.db for database")
    except KeyboardInterrupt:
        print("\n\n⚠️ Scraping interrupted by user.")
        scraper.save_data()
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        raise
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
