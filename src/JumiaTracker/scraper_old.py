import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

# --- CONFIGURATION: THE JUMIA MAP ---
# We define categories and their base URLs for page 1
JUMIA_CATEGORIES = {
    "Appliances": {
        "Microwaves": "https://www.jumia.ug/microwaves/",
        "Refrigerators": "https://www.jumia.ug/refrigerators/",
        "Blenders": "https://www.jumia.ug/blenders/",
        # Add others here...
    },
    "Computing": {
        "Laptops": "https://www.jumia.ug/laptops/",
        "Printers": "https://www.jumia.ug/printers-scanners/",
        # Add others here...
    },
    # Add the rest of your categories map here...
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

# To store all scraped data
all_products_data = []