from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import random
import time

class ShareHandler:
    def __init__(self, driver, history_manager=None):  # Add history_manager parameter
        self.driver = driver
        self.max_retries = 2
        self.history_manager = history_manager

    def share_post_with_users(self, post_url, users):
        successful_shares = []
        print(f"\n[DEBUG] Starting individual shares for {len(users)} users")
        
        for index, username in enumerate(users, 1):
            try:
                # Skip if already shared with this user
                if self.history_manager and self.history_manager.has_shared_with_user(username, post_url):
                    print(f"[INFO] Skipping {username} - already received this post")
                    continue

                print(f"\n[DEBUG] Processing user {index}/{len(users)}: {username}")
                
                # Go to post for each user
                self.driver.get(post_url)
                time.sleep(2 + random.uniform(1, 2))  # Random delay

                # Click share button
                share_btn = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "button._abl-"))
                )
                self.driver.execute_script("arguments[0].click();", share_btn)
                time.sleep(1 + random.uniform(0.5, 1.5))

                # Find and clear search input
                search_input = WebDriverWait(self.driver, 4).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='Search']"))
                )
                search_input.clear()
                time.sleep(1)

                # Search for single user
                search_input.send_keys(username)
                print(f"[DEBUG] Searching for user: {username}")
                time.sleep(2 + random.uniform(1, 2))

                if self._select_single_user(username):
                    if self._click_and_verify_send():
                        successful_shares.append(username)
                        print(f"[DEBUG] Successfully shared with {username}")
                        delay = random.uniform(2, 5)  # Random delay between shares
                        print(f"[DEBUG] Waiting {delay:.1f} seconds before next share...")
                        time.sleep(delay)
                    else:
                        print(f"[WARNING] Failed to send to {username}")
                else:
                    print(f"[WARNING] Could not select user {username}")

            except Exception as e:
                print(f"[ERROR] Error processing {username}: {e}")
                continue

        return successful_shares

    def _select_single_user(self, username):
        """Select a single user from search results"""
        try:
            user_selectors = [
                f"//div[@role='dialog']//div[contains(text(), '{username}')]",
                f"//div[contains(@class, '_abm0')]//div[contains(text(), '{username}')]",
                f"//div[contains(@class, 'x1i10hfl')]//div[contains(text(), '{username}')]",
                "//div[@role='dialog']//div[contains(@class, '_aacl')]",
                f"//div[contains(@role, 'button')]//div[contains(text(), '{username}')]"
            ]

            user_selected = False
            for selector in user_selectors:
                try:
                    print(f"[DEBUG] Trying selector: {selector}")
                    elements = self.driver.find_elements(By.XPATH, selector)
                    
                    if elements:
                        print(f"[DEBUG] Found {len(elements)} potential matches")
                        for element in elements:
                            try:
                                if username.lower() in element.text.lower():
                                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                                    time.sleep(2)
                                    element.click()
                                    user_selected = True
                                    print(f"[DEBUG] Successfully selected user: {username}")
                                    time.sleep(1)
                                    return True
                            except:
                                continue

                except Exception as e:
                    print(f"[DEBUG] Selector {selector} failed: {str(e)}")
                    continue

            if not user_selected:
                # Try checkbox selectors as fallback
                checkbox_selectors = [
                    "//div[@role='dialog']//input[@type='checkbox']",
                    "//div[@role='dialog']//div[@role='checkbox']",
                    f"//label[contains(., '{username}')]//input"
                ]
                
                for selector in checkbox_selectors:
                    try:
                        elements = self.driver.find_elements(By.XPATH, selector)
                        for element in elements:
                            if element.is_displayed():
                                element.click()
                                user_selected = True
                                print(f"[DEBUG] Selected user via checkbox: {username}")
                                time.sleep(1)
                                return True
                    except:
                        continue

            return False

        except Exception as e:
            print(f"[DEBUG] User selection failed: {e}")
            return False

    def _click_and_verify_send(self):
        """Click send button and verify send for single user"""
        try:
            send_selectors = [
                "//div[text()='Send']", 
                "//div[@role='dialog']//div[text()='Send']",
                "//div[contains(text(), 'Send')]",
                "//div[contains(@class, 'x1i10hfl') and text()='Send']",
                "//div[@role='dialog']//div[contains(@class, 'x1i10hfl') and text()='Send']"
            ]

            for selector in send_selectors:
                try:
                    send_buttons = self.driver.find_elements(By.XPATH, selector)
                    for btn in send_buttons:
                        if btn.is_displayed() and btn.is_enabled():
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                            time.sleep(2)
                            try:
                                btn.click()
                                print("[DEBUG] Successfully clicked send button")
                                time.sleep(3)
                                return True
                            except:
                                continue
                except:
                    continue

            return False

        except Exception as e:
            print(f"[DEBUG] Send verification failed: {e}")
            return False