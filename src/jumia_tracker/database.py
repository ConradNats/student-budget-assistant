\"\"\"Database module for storing scraped Jumia product data.\"\"\"

import json
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd


class JumiaDatabase:
    def __init__(self, db_path: str = \"data/processed/jumia_tracker.db\"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = None
        self.init_database()

    def init_database(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        cursor.execute(\"\"\"
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_url TEXT UNIQUE,
                product_name TEXT NOT NULL,
                main_category TEXT,
                sub_category TEXT,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        \"\"\")
        cursor.execute(\"\"\"
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                price_ugx INTEGER NOT NULL,
                rating REAL,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        \"\"\")
        cursor.execute(\"CREATE INDEX IF NOT EXISTS idx_price_history_product_id ON price_history(product_id)\")
        cursor.execute(\"CREATE INDEX IF NOT EXISTS idx_price_history_scraped_at ON price_history(scraped_at)\")
        cursor.execute(\"CREATE INDEX IF NOT EXISTS idx_products_url ON products(product_url)\")
        self.conn.commit()

    def upsert_product(self, product_data: Dict) -> int:
        cursor = self.conn.cursor()
        product_url = product_data.get('Product_URL') or product_data.get('product_url')
        product_name = product_data.get('Product_Name') or product_data.get('product_name')
        main_category = product_data.get('Main_Category') or product_data.get('main_category')
        sub_category = product_data.get('Sub_Category') or product_data.get('sub_category')
        if not product_url:
            product_url = f\"name:{product_name}:{main_category}:{sub_category}\"
        cursor.execute(\"SELECT id FROM products WHERE product_url = ?\", (product_url,))
        result = cursor.fetchone()
        if result:
            product_id = result['id']
            cursor.execute(\"UPDATE products SET last_seen = CURRENT_TIMESTAMP WHERE id = ?\", (product_id,))
        else:
            cursor.execute(\"\"\"
                INSERT INTO products (product_url, product_name, main_category, sub_category)
                VALUES (?, ?, ?, ?)
            \"\"\", (product_url, product_name, main_category, sub_category))
            product_id = cursor.lastrowid
        self.conn.commit()
        return product_id

    def add_price_record(self, product_id: int, price: int, rating: float = 0.0):
        cursor = self.conn.cursor()
        cursor.execute(\"INSERT INTO price_history (product_id, price_ugx, rating) VALUES (?, ?, ?)\",
                       (product_id, price, rating))
        self.conn.commit()

    def save_products(self, products: List[Dict]) -> int:
        count = 0
        for product in products:
            try:
                price = product.get('Price_UGX') or product.get('price_ugx', 0)
                if price <= 0:
                    continue
                product_id = self.upsert_product(product)
                rating = product.get('Rating') or product.get('rating', 0.0)
                self.add_price_record(product_id, price, rating)
                count += 1
            except Exception as e:
                print(f\"Error saving product to DB: {e}\")
                continue
        return count

    def get_price_history(self, product_url: str = None, days: int = 7) -> pd.DataFrame:
        cursor = self.conn.cursor()
        if product_url:
            query = \"\"\"
                SELECT p.product_name, p.main_category, p.sub_category, p.product_url,
                       ph.price_ugx, ph.rating, ph.scraped_at
                FROM price_history ph
                JOIN products p ON p.id = ph.product_id
                WHERE p.product_url = ?
                AND datetime(ph.scraped_at) >= datetime('now', '-' || ? || ' days')
                ORDER BY ph.scraped_at ASC
            \"\"\"
            cursor.execute(query, (product_url, days))
        else:
            query = \"\"\"
                SELECT p.product_name, p.main_category, p.sub_category, p.product_url,
                       ph.price_ugx, ph.rating, ph.scraped_at
                FROM price_history ph
                JOIN products p ON p.id = ph.product_id
                WHERE datetime(ph.scraped_at) >= datetime('now', '-' || ? || ' days')
                ORDER BY ph.scraped_at DESC
            \"\"\"
            cursor.execute(query, (days,))
        rows = cursor.fetchall()
        if not rows:
            return pd.DataFrame()
        df = pd.DataFrame([dict(row) for row in rows])
        return df

    def get_latest_prices(self) -> pd.DataFrame:
        query = \"\"\"
            SELECT p.product_name, p.main_category, p.sub_category, p.product_url,
                   ph.price_ugx, ph.rating, ph.scraped_at
            FROM price_history ph
            JOIN products p ON p.id = ph.product_id
            WHERE ph.id IN (SELECT MAX(id) FROM price_history GROUP BY product_id)
            ORDER BY ph.scraped_at DESC
        \"\"\"
        df = pd.read_sql_query(query, self.conn)
        return df

    def export_to_csv(self, output_path: str = None, days: int = None):
        if days:
            df = self.get_price_history(days=days)
        else:
            query = \"\"\"
                SELECT p.product_name, p.main_category, p.sub_category, p.product_url,
                       ph.price_ugx, ph.rating, ph.scraped_at
                FROM price_history ph
                JOIN products p ON p.id = ph.product_id
                ORDER BY ph.scraped_at DESC
            \"\"\"
            df = pd.read_sql_query(query, self.conn)
        if output_path is None:
            timestamp = datetime.now().strftime(\"%Y%m%d_%H%M%S\")
            output_path = f\"data/raw/jumia_prices_{timestamp}.csv\"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f\"Exported {len(df)} records to {output_path}\")
        return df

    def export_to_json(self, output_path: str = None, days: int = None):
        if days:
            df = self.get_price_history(days=days)
        else:
            query = \"\"\"
                SELECT p.product_name, p.main_category, p.sub_category, p.product_url,
                       ph.price_ugx, ph.rating, ph.scraped_at
                FROM price_history ph
                JOIN products p ON p.id = ph.product_id
                ORDER BY ph.scraped_at DESC
            \"\"\"
            df = pd.read_sql_query(query, self.conn)
        if output_path is None:
            timestamp = datetime.now().strftime(\"%Y%m%d_%H%M%S\")
            output_path = f\"data/raw/jumia_prices_{timestamp}.json\"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        records = df.to_dict('records')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=2, default=str)
        print(f\"Exported {len(records)} records to {output_path}\")
        return records

    def get_stats(self):
        cursor = self.conn.cursor()
        cursor.execute(\"SELECT COUNT(*) as count FROM products\")
        products_count = cursor.fetchone()['count']
        cursor.execute(\"SELECT COUNT(*) as count FROM price_history\")
        history_count = cursor.fetchone()['count']
        cursor.execute(\"SELECT COUNT(DISTINCT DATE(scraped_at)) as days FROM price_history\")
        days_count = cursor.fetchone()['days']
        print(\"\n=== Database Statistics ===\")
        print(f\"Total unique products: {products_count}\")
        print(f\"Total price records: {history_count}\")
        print(f\"Days with data: {days_count}\")
        print(\"=\" * 30)
        return {'products': products_count, 'price_records': history_count, 'days_tracked': days_count}

    def close(self):
        if self.conn:
            self.conn.close()
