"""Web scraper for Jumia Uganda product prices."""

import json
import os
import random
import time
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup

from . import config
from .database import JumiaDatabase


class JumiaScraper:
    """Scraper for Jumia Uganda e-commerce platform."""
    
    def __init__(self, headers: Optional[Dict] = None, delay_range: tuple = (2, 4),
                 save_to_db: bool = True, db_path: str = "data/processed/jumia_tracker.db"):
        """
        Initialize the scraper.
        
        Args:
            headers: HTTP headers to use for requests
            delay_range: Tuple of (min, max) seconds to wait between requests
            save_to_db: Whether to automatically save to database
            db_path: Path to SQLite database
        """
        self.headers = headers or config.HEADERS
        self.delay_range = delay_range
        self.products_data = []
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.save_to_db = save_to_db
        self.db = JumiaDatabase(db_path) if save_to_db else None
        self.scrape_timestamp = datetime.now()
    
    def _polite_delay(self):
        """Add a random delay to be polite to the server."""
        time.sleep(random.uniform(*self.delay_range))
    
    def scrape_category_page(self, url: str, main_cat: str, sub_cat: str) -> Optional[str]:
        """
        Scrape a single page of product listings.
        
        Args:
            url: URL of the page to scrape
            main_cat: Main category name
            sub_cat: Sub-category name
            
        Returns:
            URL of next page if exists, None otherwise
        """
        print(f"--- Scraping: {sub_cat} in {main_cat} ---")
        
        try:
            self._polite_delay()
            response = self.session.get(url, timeout=config.TIMEOUT)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Jumia product listings are usually inside articles with class 'prd'
            products = soup.find_all("article", class_="prd")
            print(f"Found {len(products)} products on this page.")
            
            for card in products:
                # Extract product name
                name_element = card.find("h3", class_="name")
                name = name_element.get_text().strip() if name_element else "Unknown"
                
                # Extract price
                price_element = card.find("div", class_="prc")
                if price_element:
                    price_str = price_element.get_text().strip()
                    # Clean price: remove currency and commas
                    price_clean = price_str.replace("USh", "").replace("UGX", "").replace(",", "").strip()
                    try:
                        price = int(price_clean)
                    except ValueError:
                        price = 0
                else:
                    price = 0
                
                # Extract rating
                rating_element = card.find("div", class_="rev")
                if rating_element:
                    rating_text = rating_element.get_text().strip().split(" ")[0]
                    try:
                        rating = float(rating_text)
                    except ValueError:
                        rating = 0.0
                else:
                    rating = 0.0
                
                # Extract product URL if available
                link_element = card.find("a", class_="core")
                product_url = None
                if link_element and link_element.get("href"):
                    product_url = urljoin("https://www.jumia.ug", link_element.get("href"))
                
                self.products_data.append({
                    "Main_Category": main_cat,
                    "Sub_Category": sub_cat,
                    "Product_Name": name,
                    "Price_UGX": price,
                    "Rating": rating,
                    "Product_URL": product_url,
                    "Scraped_At": self.scrape_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "Scrape_Date": self.scrape_timestamp.strftime("%Y-%m-%d")
                })
            
            # Check for pagination
            next_button = soup.find("a", {"aria-label": "Next Page"})
            if next_button and next_button.get("href"):
                relative_url = next_button.get("href")
                next_url = urljoin("https://www.jumia.ug", relative_url)
                return next_url
            
            return None
            
        except requests.RequestException as e:
            print(f"Request error scraping {url}: {e}")
            return None
        except Exception as e:
            print(f"Error scraping page {url}: {e}")
            return None
    
    def scrape_category(self, sub_cat: str, base_url: str, main_cat: str = "", 
                       max_pages: Optional[int] = None) -> List[Dict]:
        """
        Scrape all pages of a category.
        
        Args:
            sub_cat: Sub-category name
            base_url: Starting URL for the category
            main_cat: Main category name
            max_pages: Maximum number of pages to scrape (None for all)
            
        Returns:
            List of product dictionaries
        """
        current_url = base_url
        page_count = 0
        
        while current_url:
            next_page_url = self.scrape_category_page(current_url, main_cat, sub_cat)
            current_url = next_page_url
            page_count += 1
            
            if max_pages and page_count >= max_pages:
                break
            
            if current_url:
                time.sleep(random.uniform(config.PAGE_DELAY_MIN, config.PAGE_DELAY_MAX))
        
        return self.products_data
    
    def scrape_all_categories(self, categories: Optional[Dict] = None, 
                             max_pages_per_category: Optional[int] = None) -> pd.DataFrame:
        """
        Scrape all categories defined in config.
        
        Args:
            categories: Category mapping (uses config if None)
            max_pages_per_category: Max pages per sub-category
            
        Returns:
            DataFrame with all scraped products
        """
        if categories is None:
            categories = config.JUMIA_CATEGORIES
        
        self.products_data = []
        self.scrape_timestamp = datetime.now()
        
        for main_category, sub_categories in categories.items():
            for sub_category, base_url in sub_categories.items():
                print(f"\n{'='*50}")
                print(f"Starting {sub_category} ({main_category})")
                print(f"{'='*50}")
                self.scrape_category(sub_category, base_url, main_category, 
                                    max_pages_per_category)
        
        return self.save_data()
    
    def save_data(self, csv_dir: str = "data/raw", json_dir: str = "data/raw",
                  save_csv: bool = True, save_json: bool = True) -> pd.DataFrame:
        """
        Save scraped data to CSV, JSON, and SQLite database with date in filename.
        
        Args:
            csv_dir: Directory for CSV files
            json_dir: Directory for JSON files
            save_csv: Whether to save CSV
            save_json: Whether to save JSON
            
        Returns:
            DataFrame of saved data
        """
        if not self.products_data:
            print("No data was scraped.")
            return pd.DataFrame()
        
        df = pd.DataFrame(self.products_data)
        # Remove products with invalid prices
        df_clean = df[df['Price_UGX'] > 0].copy()
        
        os.makedirs(csv_dir, exist_ok=True)
        os.makedirs(json_dir, exist_ok=True)
        
        timestamp_str = self.scrape_timestamp.strftime("%Y%m%d_%H%M%S")
        date_str = self.scrape_timestamp.strftime("%Y-%m-%d")
        
        # Save to CSV with date
        if save_csv:
            csv_path = os.path.join(csv_dir, f"jumia_prices_{timestamp_str}.csv")
            df_clean.to_csv(csv_path, index=False)
            print(f"Saved CSV: {csv_path} ({len(df_clean)} products)")
            # Also save a dated copy
            csv_dated_path = os.path.join(csv_dir, f"jumia_prices_{date_str}.csv")
            df_clean.to_csv(csv_dated_path, index=False)
            print(f"Saved dated CSV: {csv_dated_path}")
        
        # Save to JSON with date
        if save_json:
            json_path = os.path.join(json_dir, f"jumia_prices_{timestamp_str}.json")
            records = df_clean.to_dict('records')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(records, f, indent=2, default=str)
            print(f"Saved JSON: {json_path} ({len(records)} products)")
            # Also save a dated copy
            json_dated_path = os.path.join(json_dir, f"jumia_prices_{date_str}.json")
            with open(json_dated_path, 'w', encoding='utf-8') as f:
                json.dump(records, f, indent=2, default=str)
            print(f"Saved dated JSON: {json_dated_path}")
        
        # Save to SQLite database
        if self.save_to_db and self.db:
            saved_count = self.db.save_products(df_clean.to_dict('records'))
            print(f"Saved to database: {saved_count} records")
            self.db.get_stats()
        
        print(f"\n{'='*50}")
        print(f"Scraping complete!")
        print(f"Total unique products saved: {len(df_clean)}")
        print(f"{'='*50}")
        
        return df_clean
    
    def get_dataframe(self) -> pd.DataFrame:
        """Get scraped data as DataFrame."""
        if not self.products_data:
            return pd.DataFrame()
        df = pd.DataFrame(self.products_data)
        return df[df['Price_UGX'] > 0].copy()
    
    def close(self):
        """Close database connection."""
        if self.db:
            self.db.close()
```
