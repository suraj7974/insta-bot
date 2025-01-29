from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time

class PostHandler:
    def __init__(self, driver, username):
        self.driver = driver
        self.username = username

    def get_my_recent_posts(self, max_posts=5):
        print(f"[DEBUG] Fetching posts from profile: {self.username}")
        
        posts = []
        try:
            # First refresh the profile page
            self.driver.get(f'https://www.instagram.com/{self.username}/')
            time.sleep(5)

            # Updated post selectors
            post_selectors = [
                "//div[@class='_aabd _aa8k _aanf']//a",
                "//article//div[contains(@class, 'x1iyjqo2')]//a",
                "//div[contains(@class, '_ac7v')]//a",
                "//article//a[contains(@href, '/p/')]"
            ]

            for selector in post_selectors:
                try:
                    elements = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_all_elements_located((By.XPATH, selector))
                    )
                    
                    if elements:
                        print(f"[DEBUG] Found {len(elements)} posts with selector: {selector}")
                        self.driver.execute_script("window.scrollTo(0, 100);")  # Slight scroll to load images
                        time.sleep(2)
                        
                        for element in elements[:max_posts]:
                            href = element.get_attribute('href')
                            if href and '/p/' in href:
                                posts.append({
                                    'url': href,
                                    'timestamp': datetime.now().isoformat()
                                })
                        if posts:
                            break
                except Exception as e:
                    print(f"[DEBUG] Selector {selector} failed: {str(e)}")
                    continue

            return posts

        except Exception as e:
            print(f"[ERROR] Failed to fetch posts: {e}")
            return []