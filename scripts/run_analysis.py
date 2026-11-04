#!/usr/bin/env python3
"""Run price analysis on scraped data."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from jumia_tracker import analyze_prices


def main():
    """Main function to run analysis."""
    csv_file = os.environ.get('CSV_FILE', 'data/raw/test_price_history.csv')
    product_name = os.environ.get('PRODUCT_NAME', 'Example Product')
    
    print(f"Analyzing: {csv_file}")
    analyze_prices(csv_file, product_name, save_path='price_history_chart.png')


if __name__ == "__main__":
    main()
