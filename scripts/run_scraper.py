#!/usr/bin/env python3
"""Run the Jumia scraper."""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

try:
    from jumia_tracker import JumiaScraper
    from jumia_tracker import config
except ImportError:
    try:
        from JumiaTracker import JumiaScraper
        from JumiaTracker import config
    except ImportError:
        raise


def main():
    """Main function to run the scraper."""
    print("Jumia Uganda Price Scraper")
    print("=" * 50)
    
    scraper = JumiaScraper()
    
    # For testing, limit to 1 page per category to avoid long runs
    max_pages = int(os.environ.get('MAX_PAGES', '1'))
    
    print(f"Scraping with max {max_pages} page(s) per category")
    print("Set MAX_PAGES=None to scrape all pages\n")
    
    try:
        df = scraper.scrape_all_categories(max_pages_per_category=max_pages)
        print(f"\nTotal products scraped: {len(df)}")
    except KeyboardInterrupt:
        print("\n\nScraping interrupted by user.")
        scraper.save_data()
    except Exception as e:
        print(f"\nError occurred: {e}")
        raise


if __name__ == "__main__":
    main()
