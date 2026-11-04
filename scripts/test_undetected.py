import undetected_chromedriver as uc
import time

options = uc.ChromeOptions()
options.headless = True
driver = uc.Chrome(options=options)
try:
    driver.get('https://www.jumia.ug/laptops/')
    time.sleep(20)
    print(driver.title)
    print(driver.page_source[:200])
except Exception as e:
    print(e)
finally:
    driver.quit()

