"""Configuration settings for Jumia scraper."""

JUMIA_CATEGORIES = {
    "Appliances": {
        "Microwaves": "https://www.jumia.ug/small-appliances-microwave/",
        "Refrigerators": "https://www.jumia.ug/freezers/",
        "Blenders": "https://www.jumia.ug/blenders/",
    },
    "Computing": {
        "Laptops": "https://www.jumia.ug/laptops/",
        "Printers": "https://www.jumia.ug/printers-scanners/",
        "Phones": "https://www.jumia.ug/phones-tablets/",
    },
    "Home & Office": {
        "Furniture": "https://www.jumia.ug/furniture/",
        "Home Decor": "https://www.jumia.ug/home-decor/",
        "Kitchen & Dining": "https://www.jumia.ug/kitchen-dining/",
    },
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Connection": "keep-alive",
}

# Default settings
DEFAULT_DELAY_MIN = 2
DEFAULT_DELAY_MAX = 4
PAGE_DELAY_MIN = 5
PAGE_DELAY_MAX = 10
MAX_PAGES_PER_CATEGORY = None  # Set to None for all pages, or a number for testing
TIMEOUT = 30
