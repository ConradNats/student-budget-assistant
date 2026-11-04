from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

TEST_URL = "https://www.jumia.ug/laptops/"

print("Starting the Ghost Browser (Selenium)...")

# --- CONFIGURE THE BROWSER ---
chrome_options = Options()
# These options help hide the fact that we are a robot
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

# Set up the driver (this automatically downloads the right Chrome driver for your PC)
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    print(f"Navigating to {TEST_URL}...")
    driver.get(TEST_URL)
    
    # Wait for the page to fully load (Wait up to 15 seconds for 'article' with class 'prd' to appear)
    print("Waiting for products to load...")
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "article.prd"))
    )
    print("✅ PAGE LOADED AND SECURITY BYPASSED.")

    # Find all products using CSS Selectors
    products = driver.find_elements(By.CSS_SELECTOR, "article.prd")
    print(f"Found {len(products)} products on the page.")

    if len(products) > 0:
        print("\n--- First Product Extracted ---")
        first_prod = products[0]
        
        # Extract Name
        try:
            name_el = first_prod.find_element(By.CSS_SELECTOR, "h3.name")
            name = name_el.text
            print(f"Product Name: {name}")
        except:
            print("❌ Could not find name")

        # Extract Price
        try:
            price_el = first_prod.find_element(By.CSS_SELECTOR, "div.prc")
            price = price_el.text
            print(f"Product Price: {price}")
        except:
            print("❌ Could not find price")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    print("\nClosing the browser in 5 seconds...")
    time.sleep(5)
    driver.quit() # Always close the browser when done
