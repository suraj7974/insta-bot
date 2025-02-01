from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def setup_driver():
    options = Options()
    options.headless = False
    # options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")  
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu") 
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    service = Service("/usr/bin/chromedriver")
    return webdriver.Chrome(service=service, options=options)
