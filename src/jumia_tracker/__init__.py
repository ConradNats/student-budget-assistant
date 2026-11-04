"""Jumia Uganda Price Tracker - A web scraping and price analysis tool for Jumia Uganda."""

__version__ = "1.0.0"
__author__ = "Student Budget Assistant"

from .analyzer import PriceAnalyzer, analyze_prices
from .database import JumiaDatabase
from .scraper import JumiaScraper

__all__ = ["JumiaScraper", "PriceAnalyzer", "analyze_prices", "JumiaDatabase"]
