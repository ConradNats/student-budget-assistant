import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))
try:
    from jumia_tracker import JumiaSeleniumScraper
except ImportError:
    try:
        from JumiaTracker import JumiaSeleniumScraper
    except ImportError:
        raise

s = JumiaSeleniumScraper(save_to_db=False, headless=True)
try:
    res = s.scrape_category_page('https://www.jumia.ug/laptops/', 'Computing', 'Laptops')
    print('NEXT:', res)
    print('COUNT:', len(s.products_data))
    if s.products_data:
        print(s.products_data[0])
    s.close()
except Exception as e:
    print('ERR', e)
    import traceback
    traceback.print_exc()
    sys.exit(1)
