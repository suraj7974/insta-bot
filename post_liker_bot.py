from dotenv import load_dotenv
from driver_setup import setup_driver
import os
import time
from modules.auth import InstagramAuth
from modules.history import HistoryManager
from modules.post_handler import PostHandler
from modules.share_handler import ShareHandler
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()

class InstagramPostLikerBot:
    def __init__(self, login_email, password, target_username=None):
        print("[DEBUG] Initializing Instagram Post Liker Bot")
        self.driver = setup_driver()
        self.login_email = login_email
        self.password = password
        self.username = target_username
        self.auth = InstagramAuth(self.driver, login_email, password)
        self.history_manager = HistoryManager()
        self.post_handler = PostHandler(self.driver, self.username)
        self.share_handler = ShareHandler(self.driver, self.history_manager)

    def get_users_from_post_likes(self, post_url, max_users=50):
        """Get users who liked a specific post"""
        try:
            print(f"[DEBUG] Getting users from post: {post_url}")
            self.driver.get(post_url)
            time.sleep(3)

            # Click on likes count to open likes modal
            likes_button_selectors = [
                "//a[contains(@href, '/liked_by/')]",
                "//button[contains(@class, '_abl-')]//span",
                "//button[contains(text(), 'others')]"
            ]

            for selector in likes_button_selectors:
                try:
                    likes_button = WebDriverWait(self.driver, 4).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    likes_button.click()
                    print("[DEBUG] Opened likes modal")
                    break
                except:
                    continue

            time.sleep(2)
            users = set()
            scroll_attempts = 0
            max_scroll_attempts = 30

            while len(users) < max_users and scroll_attempts < max_scroll_attempts:
                # Get usernames from current view
                username_selectors = [
                    "//div[@role='dialog']//a[contains(@class, 'notranslate')]",
                    "//div[@role='dialog']//a[contains(@href, '/')]//span",
                    "//div[contains(@class, '_aacl')]//a"
                ]

                for selector in username_selectors:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        try:
                            username = element.text.strip()
                            if username and username != self.username:
                                users.add(username)
                        except:
                            continue

                print(f"[DEBUG] Found {len(users)} users so far")

                # Scroll the modal
                self.driver.execute_script(
                    "document.querySelector('div[role=\"dialog\"]').scrollTop += 300"
                )
                time.sleep(1)
                scroll_attempts += 1

            print(f"[DEBUG] Found total {len(users)} unique users")
            return list(users)

        except Exception as e:
            print(f"[ERROR] Failed to get users from post: {e}")
            return []

def main():
    login_email = os.getenv('INSTA_ID')
    password = os.getenv('INSTA_PASSWORD')
    target_username = os.getenv('TARGET_USERNAME')
    
    if not login_email or not password:
        raise ValueError("Instagram credentials not found in .env file")

    # Post URL to get likers from
    target_post_url = "https://www.instagram.com/p/DFfIvPeOvPe/?igsh=MWRjdWMyd3lkNzZrZg=="  # Replace with actual post URL
    
    sender = InstagramPostLikerBot(login_email, password, target_username)
    
    try:
        sender.auth.login()
        time.sleep(2)
        
        # Get users from post likes
        print("\n[STEP 1] Getting users from post likes")
        users = sender.get_users_from_post_likes(target_post_url, max_users=50)
        if not users:
            print("[ERROR] No users found")
            return
        
        # Randomize user order
        users = list(users)
        random.shuffle(users)
        print(f"Found {len(users)} users (randomized)")
        
        # Get your post to share
        print("\n[STEP 2] Getting recent posts")
        recent_posts = sender.post_handler.get_my_recent_posts(max_posts=1)
        if not recent_posts:
            print("[ERROR] No posts found to share")
            return
        
        # Filter and share
        latest_post = recent_posts[0]
        filtered_users = [
            user for user in users 
            if not sender.history_manager.has_shared_with_user(user, latest_post['url'])
        ]
        
        if not filtered_users:
            print("[INFO] All users have already received this post")
            return
            
        print(f"Found {len(filtered_users)} users who haven't received this post")
        print(f"\n[STEP 3] Starting individual shares for post: {latest_post['url']}")
        
        successful_users = sender.share_handler.share_post_with_users(latest_post['url'], filtered_users)
        
        # Update history
        for user in successful_users:
            sender.history_manager.update_history(user, latest_post['url'])
        
        print(f"\nCompleted! Successfully shared with {len(successful_users)} users")
        print("Browser will remain open. Press Ctrl+C to close.")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nClosing browser...")
        sender.driver.quit()
    except Exception as e:
        print(f"\nError occurred: {e}")
        sender.driver.quit()

if __name__ == "__main__":
    main()
