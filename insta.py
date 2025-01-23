from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import os
from dotenv import load_dotenv
from driver_setup import setup_driver

# Load environment variables at the top
load_dotenv()

class InstagramMessageSender:
    def __init__(self, username, password):
        print("[DEBUG] Initializing Instagram Message Sender")
        self.driver = setup_driver()
        self.username = username
        self.password = password

    def login(self):
        print("[DEBUG] Attempting to login to Instagram")
        self.driver.get('https://www.instagram.com')
        time.sleep(2)

        # Login process
        try:
            username_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_input = self.driver.find_element(By.NAME, "password")
            
            username_input.send_keys(self.username)
            password_input.send_keys(self.password)
            password_input.submit()
            
            # Wait for login to complete
            time.sleep(5)
            print("[DEBUG] Login successful")
        except Exception as e:
            print(f"[ERROR] Login failed: {e}")
            raise

    def find_users_by_hashtag(self, hashtag, max_users=10):
        print(f"[DEBUG] Searching users with hashtag #{hashtag}")
        self.driver.get(f'https://www.instagram.com/explore/tags/{hashtag}/')
        time.sleep(5)  # Wait for initial load
        
        users = set()
        try:
            # Scroll down to load more posts
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Wait for posts to load
            posts = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "._aagv"))
            )
            print(f"[DEBUG] Found {len(posts)} posts")
            
            if posts:
                # Use JavaScript to click the first post
                try:
                    self.driver.execute_script("arguments[0].click();", posts[0])
                    time.sleep(3)
                except Exception as e:
                    print(f"[DEBUG] Failed to click first post with JS: {str(e)}")
                    # Fallback: try clicking with ActionChains
                    from selenium.webdriver.common.action_chains import ActionChains
                    actions = ActionChains(self.driver)
                    actions.move_to_element(posts[0]).click().perform()
                    time.sleep(3)

            # Collect users from posts
            for _ in range(max_users):
                try:
                    # Try multiple selectors for username
                    username_selectors = [
                        "._aaqt", 
                        "article header a",
                        "article ._ab8w ._aaqt",
                        "header a.notranslate"
                    ]
                    
                    username = None
                    for selector in username_selectors:
                        try:
                            username_element = WebDriverWait(self.driver, 3).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                            )
                            username = username_element.text.strip()
                            if username:
                                break
                        except:
                            continue
                    
                    if username:
                        print(f"[DEBUG] Found user: {username}")
                        users.add(username)
                    
                    # Try multiple selectors for next button
                    next_button_selectors = [
                        "._aaqg button",
                        "button._abl-",
                        "svg[aria-label='Next']",
                        "button.coreSpriteRightPaginationArrow"
                    ]
                    
                    clicked = False
                    for selector in next_button_selectors:
                        try:
                            next_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                            self.driver.execute_script("arguments[0].click();", next_button)
                            clicked = True
                            break
                        except:
                            continue
                    
                    if not clicked:
                        print("[DEBUG] Could not find next button")
                        break
                        
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"[DEBUG] Error processing post: {str(e)}")
                    break

        except Exception as e:
            print(f"[ERROR] Error finding users: {str(e)}")
        
        print(f"[DEBUG] Total unique users found: {len(users)}")
        return list(users)

    def send_message(self, username, message):
        try:
            print(f"[DEBUG] Attempting to send message to {username}")
            # Navigate to direct messages
            self.driver.get('https://www.instagram.com/direct/new/')
            time.sleep(3)

            # Handle potential "Not Now" button for notifications
            try:
                not_now_button = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, "//button[text()='Not Now']"))
                )
                not_now_button.click()
                time.sleep(1)
            except:
                pass

            # Search for user with updated selector
            search_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='Search']"))
            )
            print("[DEBUG] Found search input")
            search_input.clear()
            search_input.send_keys(username)
            time.sleep(3)

            # Updated selectors for user selection
            try:
                user_selectors = [
                    "div[role='button']",
                    "div.x9f619.x1n2onr6.x1ja2u2z",
                    f"//div[contains(text(), '{username}')]",
                    ".-qQT3"
                ]
                
                user_found = False
                for selector in user_selectors:
                    try:
                        if selector.startswith("//"):
                            user_element = WebDriverWait(self.driver, 3).until(
                                EC.element_to_be_clickable((By.XPATH, selector))
                            )
                        else:
                            user_element = WebDriverWait(self.driver, 3).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                            )
                        self.driver.execute_script("arguments[0].click();", user_element)
                        user_found = True
                        print(f"[DEBUG] Selected user using selector: {selector}")
                        break
                    except:
                        continue

                if not user_found:
                    raise Exception("Could not select user")

                time.sleep(2)

                # Click "Next" or "Chat" button
                next_button_selectors = [
                    "button[type='button']",
                    "div[role='button']",
                    "//div[contains(text(), 'Next')]",
                    "//div[contains(text(), 'Chat')]"
                ]

                for selector in next_button_selectors:
                    try:
                        if selector.startswith("//"):
                            next_button = WebDriverWait(self.driver, 3).until(
                                EC.element_to_be_clickable((By.XPATH, selector))
                            )
                        else:
                            next_button = WebDriverWait(self.driver, 3).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                            )
                        self.driver.execute_script("arguments[0].click();", next_button)
                        print("[DEBUG] Clicked next button")
                        break
                    except:
                        continue

                time.sleep(2)

                # Send message with updated selector
                message_input_selectors = [
                    "textarea[placeholder*='Message']",
                    "div[contenteditable='true']",
                    "[placeholder*='Message']"
                ]

                message_sent = False
                for selector in message_input_selectors:
                    try:
                        message_input = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        message_input.clear()
                        message_input.send_keys(message)
                        time.sleep(1)
                        
                        # Try to find and click send button
                        send_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                        self.driver.execute_script("arguments[0].click();", send_button)
                        
                        message_sent = True
                        print(f"[DEBUG] Message sent to {username}")
                        break
                    except:
                        continue

                if not message_sent:
                    raise Exception("Could not send message")

            except Exception as e:
                print(f"[DEBUG] Error in user selection/message sending: {str(e)}")
                raise

        except Exception as e:
            print(f"[ERROR] Failed to send message to {username}: {str(e)}")
        
        finally:
            time.sleep(2)

    def close(self):
        if self.driver:
            print("[DEBUG] Closing WebDriver")
            self.driver.quit()

def main():
    # Get credentials from environment variables
    username = os.getenv('INSTA_ID')
    password = os.getenv('INSTA_PASSWORD')
    
    if not username or not password:
        raise ValueError("Instagram credentials not found in .env file")
    
    hashtag = "tatamarathon"  # Replace with your target hashtag
    message = "Hello! I saw your post and wanted to connect!"  # Your message

    sender = InstagramMessageSender(username, password)
    try:
        sender.login()
        users = sender.find_users_by_hashtag(hashtag, max_users=5)
        print(f"[DEBUG] Found {len(users)} users")
        
        for user in users:
            sender.send_message(user, message)
            time.sleep(30)  # Delay between messages to avoid spam detection
            
    finally:
        sender.close()

if __name__ == "__main__":
    main()
