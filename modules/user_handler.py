from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class UserHandler:
    def __init__(self, driver, username, history_manager=None):  # Add history_manager parameter
        self.driver = driver
        self.username = username
        self.history_manager = history_manager  # Store history manager

    def find_users_by_hashtag(self, hashtag, max_users=4, post_url=None):  # Add post_url parameter
        print(f"[DEBUG] Searching users with hashtag #{hashtag}")
        try:
            self.driver.get(f'https://www.instagram.com/explore/tags/{hashtag}/')
            time.sleep(5)  # Increased wait time for hashtag page load
            
            # Add error handling for hashtag not found or restricted
            error_selectors = [
                "//h2[contains(text(), 'Sorry')]",
                "//h2[contains(text(), 'restricted')]",
                "//h2[contains(text(), 'No posts')]"
            ]
            
            for selector in error_selectors:
                try:
                    error = self.driver.find_element(By.XPATH, selector)
                    if error.is_displayed():
                        print(f"[WARNING] Hashtag #{hashtag} might be restricted or have no posts")
                        return []
                except:
                    continue

            users = set()
            skipped_users = 0
            try:
                # First scroll to load more posts
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)

                # Click first post to open overlay
                first_post_selectors = [
                    "//div[contains(@class, '_aagw')]",
                    "//article//div[contains(@class, '_aagv')]",
                    "//article//a[contains(@href, '/p/')]"
                ]
                
                post_clicked = False
                for selector in first_post_selectors:
                    try:
                        first_post = WebDriverWait(self.driver, 2).until(
                            EC.presence_of_element_located((By.XPATH, selector))
                        )
                        self.driver.execute_script("arguments[0].click();", first_post)
                        post_clicked = True
                        print("[DEBUG] Clicked first post")
                        time.sleep(1)
                        break
                    except:
                        continue

                if not post_clicked:
                    raise Exception("Could not click first post")

                attempts = 0
                max_attempts = max_users * 5  # Increased to account for skipped users

                while len(users) < max_users and attempts < max_attempts:
                    try:
                        # Try to get username from the current post
                        username_selectors = [
                            "//header//a[contains(@role, 'link')]",
                            "//div[contains(@class, '_aaqt')]//a",
                            "//article//header//a"
                        ]
                        
                        username_found = False
                        for selector in username_selectors:
                            try:
                                username_element = WebDriverWait(self.driver, 3).until(
                                    EC.presence_of_element_located((By.XPATH, selector))
                                )
                                username = username_element.text.strip()
                                
                                if username and username != self.username:
                                    # Check history before adding user
                                    if self.history_manager and post_url and self.history_manager.has_shared_with_user(username, post_url):
                                        print(f"[DEBUG] Skipping {username} - already in history")
                                        skipped_users += 1
                                    else:
                                        print(f"[DEBUG] Found user: {username}")
                                        users.add(username)
                                        username_found = True
                                        break
                            except:
                                continue

                        if username_found:
                            print(f"[DEBUG] Current user count: {len(users)}")
                        
                        # Click next with updated selectors
                        next_selectors = [
                            "//button[@aria-label='Next']",
                            "//div[@class=' _aaqg _aaqh']//button",
                            "//button[contains(@class, '_abl-')]"
                        ]
                        
                        next_clicked = False
                        for selector in next_selectors:
                            try:
                                next_button = WebDriverWait(self.driver, 1).until(
                                    EC.element_to_be_clickable((By.XPATH, selector))
                                )
                                next_button.click()
                                next_clicked = True
                                print("[DEBUG] Clicked next post")
                                time.sleep(2)
                                break
                            except:
                                continue

                        if not next_clicked:
                            print("[DEBUG] Could not find next button, trying JavaScript click")
                            try:
                                self.driver.execute_script(
                                    "document.querySelector('button[aria-label=\"Next\"]').click();"
                                )
                                next_clicked = True
                                time.sleep(1)
                            except:
                                break

                        attempts += 1
                        
                    except Exception as e:
                        print(f"[DEBUG] Error in attempt {attempts}: {str(e)}")
                        attempts += 1
                        continue

                print(f"[DEBUG] Found {len(users)} unique users, skipped {skipped_users} users")
                return list(users)
                
            except Exception as e:
                print(f"[ERROR] Error finding users: {e}")
                return list(users)
        except Exception as e:
            print(f"[ERROR] Error loading hashtag page: {e}")
            return []