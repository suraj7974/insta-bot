from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import os
from dotenv import load_dotenv
from driver_setup import setup_driver
import json
from datetime import datetime
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

load_dotenv()

class InstagramMessageSender:
    def __init__(self, login_email, password):
        print("[DEBUG] Initializing Instagram Message Sender")
        self.driver = setup_driver()
        self.login_email = login_email
        self.password = password
        self.username = "kamalmarbal11"
        self.history_file = 'sent_posts_history.json'
        self.sent_history = self._load_history()
        self.profile_found = True

    def _load_history(self):
        try:
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"users": {}}

    def _save_history(self):
        with open(self.history_file, 'w') as f:
            json.dump(self.sent_history, f, indent=4)

    def login(self):
        print("[DEBUG] Attempting to login to Instagram")
        self.driver.get('https://www.instagram.com')
        time.sleep(3)

        try:
            # Handle cookie accept if present
            try:
                cookie_button = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Allow')]"))
                )
                cookie_button.click()
                time.sleep(1)
            except:
                pass

            # Login steps
            username_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_input = self.driver.find_element(By.NAME, "password")
            
            username_input.send_keys(self.login_email)
            password_input.send_keys(self.password)
            password_input.submit()
            time.sleep(5)

            # Handle notifications popup
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[text()='Not Now']"))
                ).click()
                time.sleep(2)
            except:
                pass

            print("[DEBUG] Login successful")
            
        except Exception as e:
            print(f"[ERROR] Login failed: {e}")
            raise

    def find_users_by_hashtag(self, hashtag, max_users=4):
        print(f"[DEBUG] Searching users with hashtag #{hashtag}")
        self.driver.get(f'https://www.instagram.com/explore/tags/{hashtag}/')
        time.sleep(2)
        
        users = set()
        try:
            # First scroll to load more posts
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

            # Click first post to open overlay
            first_post_selectors = [
                "//div[contains(@class, '_aagw')]",
                "//article//div[contains(@class, '_aagv')]",
                "//article//a[contains(@href, '/p/')]"
            ]
            
            post_clicked = False
            for selector in first_post_selectors:
                try:
                    first_post = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    self.driver.execute_script("arguments[0].click();", first_post)
                    post_clicked = True
                    print("[DEBUG] Clicked first post")
                    time.sleep(3)
                    break
                except:
                    continue

            if not post_clicked:
                raise Exception("Could not click first post")

            attempts = 0
            max_attempts = max_users * 3  # Allow more attempts to find users

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
                            next_button = WebDriverWait(self.driver, 5).until(
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
                            time.sleep(2)
                        except:
                            break

                    attempts += 1
                    
                except Exception as e:
                    print(f"[DEBUG] Error in attempt {attempts}: {str(e)}")
                    attempts += 1
                    continue

            print(f"[DEBUG] Found {len(users)} unique users after {attempts} attempts")
            return list(users)
            
        except Exception as e:
            print(f"[ERROR] Error finding users: {e}")
            return list(users)

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

    def send_post(self, username, post_url):
        try:
            print(f"[DEBUG] Attempting to send post to {username}")
            
            # First get the post link
            self.driver.get(post_url)
            time.sleep(3)
            
            # Click more options (three dots)
            more_options_selectors = [
                "//div[@role='button'][contains(@class, '_abl-')]",
                "//button[contains(@class, '_abl-')]",
                "//*[local-name()='svg'][@aria-label='More']"
            ]
            
            for selector in more_options_selectors:
                try:
                    more_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    more_button.click()
                    print("[DEBUG] Clicked more options")
                    time.sleep(2)
                    break
                except:
                    continue

            # Click "Copy Link" option
            copy_link_selectors = [
                "//button[text()='Copy link']",
                "//div[text()='Copy link']",
                "//button[contains(text(), 'Copy')]"
            ]
            
            for selector in copy_link_selectors:
                try:
                    copy_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    copy_button.click()
                    print("[DEBUG] Copied post link")
                    time.sleep(2)
                    break
                except:
                    continue

            # Navigate to user's DM
            self.driver.get(f'https://www.instagram.com/{username}/')
            time.sleep(3)

            # Click Message button
            message_selectors = [
                "//div[text()='Message']",
                "//button[contains(text(), 'Message')]",
                "//a[contains(@href, '/direct/')]"
            ]
            
            for selector in message_selectors:
                try:
                    message_btn = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    message_btn.click()
                    print("[DEBUG] Clicked message button")
                    time.sleep(3)
                    break
                except:
                    continue

            # Find message input and paste link
            message_input_selectors = [
                "//div[@contenteditable='true']",
                "//textarea[@placeholder='Message...']",
                "//div[@role='textbox']"
            ]
            
            for selector in message_selectors:
                try:
                    message_input = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    # Paste the copied link
                    message_input.send_keys(post_url)
                    time.sleep(1)
                    # Press Enter to send
                    message_input.send_keys(Keys.RETURN)
                    print("[DEBUG] Sent message with post link")
                    time.sleep(2)
                    return True
                except:
                    continue

            return False

        except Exception as e:
            print(f"[ERROR] Failed to send post to {username}: {e}")
            return False

    def share_post_with_users(self, post_url, users):
        try:
            print(f"\n[DEBUG] Sharing post {post_url}")
            self.driver.get(post_url)
            time.sleep(5)

            # Click share button (paper airplane icon)
            share_btn = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button._abl-"))
            )
            self.driver.execute_script("arguments[0].click();", share_btn)
            print("[DEBUG] Clicked share button")
            time.sleep(3)

            # Find search input
            search_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='Search']"))
            )
            print("[DEBUG] Found search input")

            successful_shares = []
            for username in users:
                try:
                    
                    # Type username and wait for search results
                    search_input.send_keys(username)
                    print(f"[DEBUG] Searching for user: {username}")
                    time.sleep(3)  # Wait longer for search results

                    # Updated user selection with more reliable selectors
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
                            # Try to find all matching elements
                            elements = self.driver.find_elements(By.XPATH, selector)
                            
                            if elements:
                                print(f"[DEBUG] Found {len(elements)} potential matches")
                                for element in elements:
                                    try:
                                        # Check if element contains exact username
                                        if username.lower() in element.text.lower():
                                            # Try multiple click methods
                                            try:
                                                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                                time.sleep(1)
                                                
                                                try:
                                                    element.click()
                                                except:
                                                    try:
                                                        self.driver.execute_script("arguments[0].click();", element)
                                                    except:
                                                        # Try clicking parent elements
                                                        parent = self.driver.execute_script(
                                                            "return arguments[0].parentNode;", element
                                                        )
                                                        if parent:
                                                            self.driver.execute_script("arguments[0].click();", parent)
                                                
                                                user_selected = True
                                                print(f"[DEBUG] Successfully selected user: {username}")
                                                break
                                            except:
                                                continue
                                            
                                    except:
                                        continue
                            
                            if user_selected:
                                break
                                
                        except Exception as e:
                            print(f"[DEBUG] Selector {selector} failed: {str(e)}")
                            continue

                    if not user_selected:
                        # Final attempt - try to find checkbox or any clickable element
                        try:
                            checkbox_selectors = [
                                "//div[@role='dialog']//input[@type='checkbox']",
                                "//div[@role='dialog']//div[@role='checkbox']",
                                f"//label[contains(., '{username}')]//input"
                            ]
                            
                            for selector in checkbox_selectors:
                                elements = self.driver.find_elements(By.XPATH, selector)
                                for element in elements:
                                    if element.is_displayed():
                                        element.click()
                                        user_selected = True
                                        print(f"[DEBUG] Selected user via checkbox: {username}")
                                        break
                                if user_selected:
                                    break
                        except:
                            pass

                    if user_selected:
                        successful_shares.append(username)
                        time.sleep(2)  # Wait between user selections
                    else:
                        print(f"[WARNING] Could not select user: {username}")

                except Exception as e:
                    print(f"[ERROR] Failed to process user {username}: {e}")
                    continue

            if successful_shares:
                # Wait for modal to be fully loaded
                time.sleep(2)
                
                # Try to find send button with new selectors and approach
                send_selectors = [
                         "//div[text()='Send']", 
                         "//div[@role='dialog']//div[text()='Send']",
                         "//div[contains(text(), 'Send')]",
                         "//div[contains(@class, 'x1i10hfl') and text()='Send']",
                         "//div[@role='dialog']//div[contains(@class, 'x1i10hfl') and text()='Send']" 
                                   ]


                send_clicked = False
                for selector in send_selectors:
                    try:
                        print(f"[DEBUG] Looking for send button with: {selector}")
                        # First find all matching elements
                        send_buttons = self.driver.find_elements(By.XPATH, selector)
                        
                        if send_buttons:
                            print(f"[DEBUG] Found {len(send_buttons)} potential send buttons")
                            # Try each found button
                            for btn in send_buttons:
                                try:
                                    # Scroll button into view
                                    self.driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                                    time.sleep(1)
                                    
                                    # Check if button is visible and enabled
                                    if btn.is_displayed() and btn.is_enabled():
                                        print("[DEBUG] Found visible and enabled send button")
                                        try:
                                            btn.click()
                                        except:
                                            self.driver.execute_script("arguments[0].click();", btn)
                                        
                                        send_clicked = True
                                        print("[DEBUG] Successfully clicked send button")
                                        time.sleep(3)
                                        break
                                except:
                                    continue
                        
                        if send_clicked:
                            break
                            
                    except Exception as e:
                        print(f"[DEBUG] Send button attempt failed: {str(e)}")
                        continue

                # Final attempt - try direct JavaScript click on any matching element
                if not send_clicked:
                    try:
                        print("[DEBUG] Attempting JavaScript click on any Send button")
                        self.driver.execute_script(
                            """
                            var buttons = document.evaluate("//div[text()='Send']", document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                            for(var i = 0; i < buttons.snapshotLength; i++) {
                                buttons.snapshotItem(i).click();
                            }
                            """
                        )
                        send_clicked = True
                        time.sleep(3)
                    except Exception as e:
                        print(f"[DEBUG] JavaScript click failed: {str(e)}")

                if not send_clicked:
                    print("[WARNING] Could not click send button with any method")
                    return []

                print(f"[DEBUG] Successfully shared with users: {successful_shares}")
                return successful_shares

            return successful_shares

        except Exception as e:
            print(f"[ERROR] Failed to share post: {e}")
            return []

    def close(self):
        if self.driver:
            print("[DEBUG] Closing WebDriver")
            self.driver.quit()

def main():
    login_email = os.getenv('INSTA_ID')
    password = os.getenv('INSTA_PASSWORD')
    
    if not login_email or not password:
        raise ValueError("Instagram credentials not found in .env file")
    
    hashtag = "photography"
    sender = InstagramMessageSender(login_email, password)
    
    try:
        sender.login()
        time.sleep(3)
        
        # First find users
        print("\n[STEP 1] Finding users from hashtag")
        users = sender.find_users_by_hashtag(hashtag, max_users=5)
        if not users:
            print("[ERROR] No users found")
            return
        print(f"Found {len(users)} users")
        
        # Then get posts
        print("\n[STEP 2] Getting recent posts from your profile")
        recent_posts = sender.get_my_recent_posts(max_posts=1)  # Get only latest post
        if not recent_posts:
            print("[ERROR] No posts found to share")
            return
        
        # Share the latest post with all users at once
        latest_post = recent_posts[0]
        print(f"\n[STEP 3] Sharing latest post: {latest_post['url']}")
        
        successful_users = sender.share_post_with_users(latest_post['url'], users)
        
        # Update history
        for user in successful_users:
            sender.sent_history["users"].setdefault(user, []).append(latest_post['url'])
        sender._save_history()
        
    finally:
        sender.close()

if __name__ == "__main__":
    main()