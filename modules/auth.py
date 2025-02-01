from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class InstagramAuth:
    def __init__(self, driver, login_email, password):
        self.driver = driver
        self.login_email = login_email
        self.password = password

    def login(self):
        print("[DEBUG] Attempting to login to Instagram")
        self.driver.get('https://www.instagram.com')
        time.sleep(1)

        try:
            # Handle cookie accept if present
            try:
                cookie_button = WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Allow')]"))
                )
                cookie_button.click()
                time.sleep(1)
            except:
                pass

            # Login steps
            username_input = WebDriverWait(self.driver, 2).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_input = self.driver.find_element(By.NAME, "password")
            
            username_input.send_keys(self.login_email)
            password_input.send_keys(self.password)
            password_input.submit()
            time.sleep(1)

            # Handle notifications popup
            try:
                WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[text()='Not Now']"))
                ).click()
                time.sleep(1)
            except:
                pass

            print("[DEBUG] Login successful")
            return True
            
        except Exception as e:
            print(f"[ERROR] Login failed: {e}")
            raise
