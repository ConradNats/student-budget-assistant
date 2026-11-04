"""Cloudscraper-based scraper for Jumia Uganda (bypasses Cloudflare)."""

import json
import os
import random
import time
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urljoin

import pandas as pd
from bs4 import BeautifulSoup

try:
    import cloudscraper
except ImportError:
    cloudscraper = None

from . import config
from .database import JumiaDatabase


class JumiaCloudScraper:
    """Cloudscraper-based scraper for Jumia Uganda."""
    
    def __init__(self, save_to_db: bool = True, db_path: str = "data/processed/jumia_tracker.db"):
        if cloudscraper is None:
            raise ImportError("cloudscraper not installed. Run: pip install cloudscraper")
        self.save_to_db = save_to_db
        self.db = JumiaDatabase(db_path) if save_to_db else None
        self.products_data = []
        self.scrape_timestamp = datetime.now()
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        self.scraper.headers.update(config.HEADERS)
    
    def _polite_delay(self):
        time.sleep(random.uniform(2, 4))
    
    def scrape_category_page(self, url: str, main_cat: str, sub_cat: str) -> Optional[str]:
        print(f"--- Scraping: {sub_cat} in {main_cat} ---")
        try:
            self._polite_delay()
            response = self.scraper.get(url, timeout=config.TIMEOUT)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            products = soup.find_all("article", class_="prd")
            print(f"Found {len(products)} products on this page.")
            for card in products:
                name_element = card.find("h3", class_="name")
                name = name_element.get_text().strip() if name_element else "Unknown"
                price_element = card.find("div", class_="prc")
                if price_element:
                    price_str = price_element.get_text().strip()
                    price_clean = price_str.replace("USh", "").replace("UGX", "").replace(",", "").strip()
                    try:
                        price = int(price_clean)
                    except ValueError:
                        price = 0
                else:
                    price = 0
                rating_element = card.find("div", class_="rev")
                if rating_element:
                    rating_text = rating_element.get_text().strip().split(" ")[0]
                    try:
                        rating = float(rating_text)
                    except ValueError:
                        rating = 0.0
                else:
                    rating = 0.0
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
            next_button = soup.find("a", {"aria-label": "Next Page"})
            if next_button and next_button.get("href"):
                relative_url = next_button.get("href")
                return urljoin("https://www.jumia.ug", relative_url)
            return None
        except Exception as e:
            print(f"Error scraping page {url}: {e}")
            return None
    
    def scrape_category(self, sub_cat: str, base_url: str, main_cat: str = "", max_pages: Optional[int] = None):
        current_url = base_url
        page_count = 0
        while current_url:
            next_page_url = self.scrape_category_page(current_url, main_cat, sub_cat)
            current_url = next_page_url
            page_count += 1
            if max_pages and page_count >= max_pages:
                break
            if current_url:
                time.sleep(random.uniform(5, 10))
        return self.products_data
    
    def scrape_all_categories(self, categories: Optional[Dict] = None, max_pages_per_category: Optional[int] = None):
        if categories is None:
            categories = config.JUMIA_CATEGORIES
        self.products_data = []
        self.scrape_timestamp = datetime.now()
        for main_category, sub_categories in categories.items():
            for sub_category, base_url in sub_categories.items():
                print(f"\n{'='*50}")
                print(f"Starting {sub_category} ({main_category})")
                print(f"{'='*50}")
                self.scrape_category(sub_category, base_url, main_category, max_pages_per_category)
        return self.save_data()
    
    def save_data(self, csv_dir: str = "data/raw", json_dir: str = "data/raw", save_csv: bool = True, save_json: bool = True):
        if not self.products_data:
            print("No data was scraped.")
            return pd.DataFrame()
        df = pd.DataFrame(self.products_data)
        df_clean = df[df['Price_UGX'] > 0].copy()
        os.makedirs(csv_dir, exist_ok=True)
        os.makedirs(json_dir, exist_ok=True)
        timestamp_str = self.scrape_timestamp.strftime("%Y%m%d_%H%M%S")
        date_str = self.scrape_timestamp.strftime("%Y-%m-%d")
        if save_csv:
            csv_path = os.path.join(csv_dir, f"jumia_prices_{timestamp_str}.csv")
            df_clean.to_csv(csv_path, index=False)
            print(f"Saved CSV: {csv_path} ({len(df_clean)} products)")
            csv_dated_path = os.path.join(csv_dir, f"jumia_prices_{date_str}.csv")
            df_clean.to_csv(csv_dated_path, index=False)
            print(f"Saved dated CSV: {csv_dated_path}")
        if save_json:
            json_path = os.path.join(json_dir, f"jumia_prices_{timestamp_str}.json")
            records = df_clean.to_dict('records')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(records, f, indent=2, default=str)
            print(f"Saved JSON: {json_path} ({len(records)} products)")
            json_dated_path = os.path.join(json_dir, f"jumia_prices_{date_str}.json")
            with open(json_dated_path, 'w', encoding='utf-8') as f:
                json.dump(records, f, indent=2, default=str)
            print(f"Saved dated JSON: {json_dated_path}")
        if self.save_to_db and self.db:
            saved_count = self.db.save_products(df_clean.to_dict('records'))
            print(f"Saved to database: {saved_count} records")
            self.db.get_stats()
        print(f"\n{'='*50}")
        print(f"Scraping complete!")
        print(f"Total unique products saved: {len(df_clean)}")
        print(f"{'='*50}")
        return df_clean
    
    def close(self):
        if self.db:
            self.db.close()
