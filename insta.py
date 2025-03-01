from dotenv import load_dotenv
from driver_setup import setup_driver
import os
import time
from modules.auth import InstagramAuth
from modules.history import HistoryManager
from modules.user_handler import UserHandler
from modules.post_handler import PostHandler
from modules.share_handler import ShareHandler
import random

load_dotenv()

class InstagramMessageSender:
    def __init__(self, login_email, password, target_username=None):
        print("[DEBUG] Initializing Instagram Message Sender")
        self.driver = setup_driver()
        self.login_email = login_email
        self.password = password
        self.username = target_username
        self.auth = InstagramAuth(self.driver, login_email, password)
        self.history_manager = HistoryManager()
        self.user_handler = UserHandler(self.driver, self.username, self.history_manager) 
        self.post_handler = PostHandler(self.driver, self.username)
        self.share_handler = ShareHandler(self.driver, self.history_manager)
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

    def find_users_from_multiple_hashtags(self, hashtags, users_per_hashtag=3, post_url=None):
        """Find users from multiple hashtags"""
        all_users = set()
        for hashtag in hashtags:
            print(f"\n[STEP] Searching hashtag: #{hashtag}")
            users = self.user_handler.find_users_by_hashtag(hashtag, max_users=users_per_hashtag, post_url=post_url)
            all_users.update(users)
            time.sleep(1) 
        return list(all_users)

    def close(self):
        if self.driver:
            print("[DEBUG] Closing WebDriver")
            self.driver.quit()

def main():
    login_email = os.getenv('INSTA_ID')
    password = os.getenv('INSTA_PASSWORD')
    target_username = os.getenv('TARGET_USERNAME')
    
    if not login_email or not password:
        raise ValueError("Instagram credentials not found in .env file")
    
    hashtags =[
  "IndiaMarathon",
  "RunIndia",
  "MarathonIndia",
  "IndianRunners",
  "RunForIndia",
  "RunningIndia",
  "DelhiMarathon",
  "MumbaiMarathon",
  "BangaloreMarathon",
  "HyderabadMarathon",
  "KolkataMarathon",
  "ChhattisgarhMarathon",
  "RaipurMarathon",
  "RunnersOfIndia",
  "RunningCoachIndia",
  "RunForFitness",
  "RunningEventIndia",
  "MarathonEventIndia",
  "RaceDayIndia",
  "RunForCauseIndia",
  "RunForCharityIndia",
  "CommunityRunIndia",
  "GreenMarathonIndia",
  "RunForNatureIndia"
]

    sender = InstagramMessageSender(login_email, password, target_username)
    
    try:
        sender.login()
        time.sleep(2)
        
        # Get posts first to have the URL for history checking
        print("\n[STEP 1] Getting recent posts")
        recent_posts = sender.get_my_recent_posts(max_posts=1)
        if not recent_posts:
            print("[ERROR] No posts found to share")
            return
        
        latest_post = recent_posts[0]
        
        # Now find users with history checking
        print("\n[STEP 2] Finding users from hashtags")
        users = sender.find_users_from_multiple_hashtags(hashtags, users_per_hashtag=10, post_url=latest_post['url'])
        if not users:
            print("[ERROR] No users found")
            return
        
        # Randomize user order
        users = list(users)
        random.shuffle(users)
        print(f"Found {len(users)} users (randomized)")
        
        # Filter out users who already received the post
        filtered_users = [
            user for user in users 
            if not sender.history_manager.has_shared_with_user(user, latest_post['url'])
        ]
        
        if not filtered_users:
            print("[INFO] All users have already received this post")
            return
            
        print(f"Found {len(filtered_users)} users who haven't received this post")
        print(f"\n[STEP 3] Starting individual shares for post: {latest_post['url']}")
        
        successful_users = sender.share_post_with_users(latest_post['url'], filtered_users)
        
        # Update history
        for user in successful_users:
            sender.history_manager.update_history(user, latest_post['url'])
            sender.history_manager._save_history()  # Save after each successful share
        
        print(f"\nCompleted! Successfully shared with {len(successful_users)} users")
        print("Browser will remain open. Press Ctrl+C to close.")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nClosing browser...")
        sender.close()
    except Exception as e:
        print(f"\nError occurred: {e}")
        sender.close()

if __name__ == "__main__":
    main()