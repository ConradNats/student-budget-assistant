"""Jumia Uganda Price Tracker - A web scraping and price analysis tool for Jumia Uganda."""

__version__ = "1.0.0"
__author__ = "Student Budget Assistant"

from .analyzer import PriceAnalyzer, analyze_prices
from .cloudscraper_scraper import JumiaCloudScraper
from .cookie_scraper import JumiaCookieScraper
from .database import JumiaDatabase
from .scraper import JumiaScraper
from .selenium_scraper import JumiaSeleniumScraper

__all__ = ["JumiaScraper", "JumiaSeleniumScraper", "JumiaCloudScraper", "JumiaCookieScraper", "PriceAnalyzer", "analyze_prices", "JumiaDatabase"]
