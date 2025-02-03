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
        
        try:
            self.driver.get(f'https://www.instagram.com/{self.username}/')
            time.sleep(3)

            # Check if profile is accessible
            error_selectors = [
                "//h2[contains(text(), 'Sorry')]",
                "//h2[contains(text(), 'Private')]",
                "//h2[contains(text(), 'No posts')]"
            ]
            
            for selector in error_selectors:
                try:
                    error = self.driver.find_element(By.XPATH, selector)
                    if error.is_displayed():
                        print(f"[ERROR] Cannot access profile {self.username}: Profile might be private or not exist")
                        return []
                except:
                    continue

            # Updated post selectors with new Instagram classes
            post_selectors = [
                "//div[contains(@class, '_ac7v')]//a[contains(@href, '/p/')]",  # Primary selector
                "//article//a[contains(@href, '/p/')]",
                "//div[contains(@style, 'flex-direction: column')]//a[contains(@href, '/p/')]",
                "//div[@class='_aagu']//a",
                "//div[contains(@class, '_aabd')]//a"
            ]

            posts = []
            for selector in post_selectors:
                try:
                    print(f"[DEBUG] Trying selector: {selector}")
                    elements = WebDriverWait(self.driver, 4).until(
                        EC.presence_of_all_elements_located((By.XPATH, selector))
                    )
                    
                    if elements:
                        print(f"[DEBUG] Found {len(elements)} potential posts")
                        # Ensure links are post links
                        for element in elements[:max_posts]:
                            href = element.get_attribute('href')
                            if href and '/p/' in href:
                                posts.append({
                                    'url': href,
                                    'timestamp': datetime.now().isoformat()
                                })
                                print(f"[DEBUG] Added post: {href}")
                        
                        if posts:
                            print(f"[DEBUG] Successfully found {len(posts)} posts")
                            return posts
                            
                except Exception as e:
                    print(f"[DEBUG] Selector {selector} failed: {str(e)}")
                    continue

            if not posts:
                print("[WARNING] No posts found with any selector")
                # Try JavaScript method as fallback
                try:
                    posts_js = self.driver.execute_script("""
                        return Array.from(document.querySelectorAll('a')).
                        filter(a => a.href.includes('/p/')).
                        slice(0, arguments[0]).
                        map(a => ({
                            url: a.href,
                            timestamp: new Date().toISOString()
                        }));
                    """, max_posts)
                    
                    if posts_js:
                        print(f"[DEBUG] Found {len(posts_js)} posts using JavaScript")
                        return posts_js

                except Exception as e:   
                           print(e)
            return []

        except Exception as e:
            print(f"[ERROR] Failed to fetch posts: {e}")
            return []