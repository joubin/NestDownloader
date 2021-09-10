from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import sys

def eprint(msg):
    sys.stderr.write(msg)


url = os.getenv('PUBLIC_URL')
if url == None or url == "":
    eprint("The URL was not set as the environmental var PUBLIC_URL")
    sys.exit(1)
fireFoxOptions = webdriver.FirefoxOptions()
fireFoxOptions.headless = True
driver = webdriver.Firefox(options=fireFoxOptions)



driver.get(url)
try:
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "video"))
    )

    for i in element.find_elements_by_css_selector("*"):
        print(i.get_attribute('src'))
finally:
    driver.quit()