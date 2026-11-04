"""Utility functions for the Jumia tracker."""

import os
from datetime import datetime


def ensure_dir(directory: str):
    """Create directory if it doesn't exist."""
    os.makedirs(directory, exist_ok=True)


def get_timestamp():
    """Get current timestamp as string."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def format_price(price: float) -> str:
    """Format price in UGX."""
    return f"{price:,.0f} UGX"
