#!/usr/bin/env python3
"""Generate test data for price analysis."""

import datetime
import os

import pandas as pd


def generate_test_data(output_path: str = "data/raw/test_price_history.csv"):
    """Generate dummy price history data."""
    # Generate last 10 days of dates
    dates = [datetime.date.today() - datetime.timedelta(days=x) for x in range(10)]
    dates.reverse()
    
    # Generate dummy prices around a hypothetical average
    prices = [950000, 980000, 1200000, 1150000, 1000000, 950000, 920000, 1300000, 1250000, 990000]
    
    data = {
        'Date': dates,
        'Price_UGX': prices
    }
    
    df = pd.DataFrame(data)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Dummy data generated in {output_path}")
    print(df)
    return df


if __name__ == "__main__":
    generate_test_data()

