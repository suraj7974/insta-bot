from dotenv import load_dotenv
from driver_setup import setup_driver
import os
import time
from modules.auth import InstagramAuth
from modules.history import HistoryManager
from modules.user_handler import UserHandler
from modules.post_handler import PostHandler
from modules.share_handler import ShareHandler

load_dotenv()

class InstagramMessageSender:
    def __init__(self, login_email, password):
        print("[DEBUG] Initializing Instagram Message Sender")
        self.driver = setup_driver()
        self.username = "kamalmarbal11"
        self.auth = InstagramAuth(self.driver, login_email, password)
        self.history_manager = HistoryManager()
        self.user_handler = UserHandler(self.driver, self.username)
        self.post_handler = PostHandler(self.driver, self.username)
        self.share_handler = ShareHandler(self.driver)
        self.profile_found = True

    def login(self):
        return self.auth.login()

    def find_users_by_hashtag(self, hashtag, max_users=4):
        return self.user_handler.find_users_by_hashtag(hashtag, max_users)

    def get_my_recent_posts(self, max_posts=5):
        return self.post_handler.get_my_recent_posts(max_posts)

    def share_post_with_users(self, post_url, users):
        return self.share_handler.share_post_with_users(post_url, users)

    def send_post(self, username, post_url):
        return self.share_handler.send_post(username, post_url)

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
            sender.history_manager.sent_history["users"].setdefault(user, []).append(latest_post['url'])
        sender.history_manager._save_history()
        
    finally:
        sender.close()

if __name__ == "__main__":
    main()