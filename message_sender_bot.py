from dotenv import load_dotenv
from driver_setup import setup_driver
import os
import time
from modules.auth import InstagramAuth
from modules.history import HistoryManager
from modules.user_handler import UserHandler
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

load_dotenv()

class InstagramMessageBot:
    def __init__(self, login_email, password, target_username=None):
        print("[DEBUG] Initializing Instagram Message Bot")
        self.driver = setup_driver()
        self.login_email = login_email
        self.password = password
        self.username = target_username
        self.auth = InstagramAuth(self.driver, login_email, password)
        self.history_manager = HistoryManager('sent_messages_history.json')  # Separate history file
        self.user_handler = UserHandler(self.driver, self.username, self.history_manager)
        self.message_templates = [
            # Template 1 - Formal and Professional
            """Hi {username}! 👋

We invite you to be part of the historic Abujhmad Marathon 2025! Experience running through the stunning landscapes of Chhattisgarh.

💫 What's special:
• Scenic beauty of Abujhmad
• Professional chip timing
• Finisher medals
• Prize pool: ₹1.5 Lakhs

Register: https://www.runabhujhmad.in
Official updates: https://www.instagram.com/abujhmadmarathon2025""",

            # Template 2 - Casual and Friendly
            """Hey {username}! 🏃‍♂️

Love running? You're going to love this! The Abujhmad Marathon 2025 is coming up, and it's not just another marathon - it's an adventure through one of India's most beautiful regions!

✨ Highlights:
- Epic running routes
- Amazing medals
- Cash prizes worth 1.5L
- Unforgettable experience

Check us out: https://www.instagram.com/abujhmadmarathon2025
Sign up: https://www.runabhujhmad.in""",

            # Template 3 - Community Focused
            """Namaste {username}! 🙏

Join the running community at Abujhmad Marathon 2025! Be part of something special as we bring together runners from across India in this unique location.

🎯 Event Features:
- Professional organization
- Chip timing
- Finisher medals
- Prizes up to ₹1,50,000

Visit https://www.runabhujhmad.in
Follow https://www.instagram.com/abujhmadmarathon2025""",

            # Template 4 - Achievement Oriented
            """Greetings {username}! 🌟

Ready for your next running milestone? The Abujhmad Marathon 2025 offers a unique opportunity to challenge yourself in one of India's most spectacular settings.

🏆 Offering:
- Professional race experience
- Chip-based timing
- Exclusive medals
- Cash prizes (1.5L)

Register now: https://www.runabhujhmad.in
Updates: https://www.instagram.com/abujhmadmarathon2025""",

            # Template 5 - Experience Focused
            """Hello {username}! 🎉

Ever dreamed of running through pristine landscapes? The Abujhmad Marathon 2025 makes it reality! Experience the beauty of Chhattisgarh while competing in a world-class event.

⭐ Highlights:
• Beautiful course
• Pro timing system
• Special medals
• Big prizes (₹1.5L)

Join us: https://www.runabhujhmad.in
Follow: https://www.instagram.com/abujhmadmarathon2025"""
        ]

    def send_promotional_message(self, username):
        """Send a personalized promotional message to a user"""
        try:
            print(f"[DEBUG] Sending message to: {username}")
            self.driver.get(f'https://www.instagram.com/{username}/')
            time.sleep(2 + random.uniform(1, 2))

            # Click Message button
            message_button_selectors = [
                "//div[text()='Message']",
                "//button[contains(text(), 'Message')]",
                "//a[contains(@href, '/direct/')]"
            ]

            for selector in message_button_selectors:
                try:
                    message_btn = WebDriverWait(self.driver, 4).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    message_btn.click()
                    print("[DEBUG] Clicked message button")
                    time.sleep(2)
                    break
                except:
                    continue

            # Find message input and send message
            message_input_selectors = [
                "//textarea[@placeholder='Message...']",
                "//div[@contenteditable='true']",
                "//div[@role='textbox']"
            ]

            # Select random message template
            message = random.choice(self.message_templates).format(username=username)

            for selector in message_input_selectors:
                try:
                    message_input = WebDriverWait(self.driver, 4).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    message_input.clear()
                    message_input.send_keys(message)
                    time.sleep(1)
                    message_input.send_keys(Keys.RETURN)
                    print(f"[DEBUG] Sent message to {username}")
                    return True
                except:
                    continue

            return False

        except Exception as e:
            print(f"[ERROR] Failed to send message to {username}: {e}")
            return False

def main():
    login_email = os.getenv('INSTA_ID')
    password = os.getenv('INSTA_PASSWORD')
    target_username = os.getenv('TARGET_USERNAME')
    
    if not login_email or not password:
        raise ValueError("Instagram credentials not found in .env file")
    
    hashtags = [
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
    
    sender = InstagramMessageBot(login_email, password, target_username)
    
    try:
        sender.auth.login()
        time.sleep(2)
        
        # Find users from hashtags
        print("\n[STEP 1] Finding users from hashtags")
        all_users = set()
        for hashtag in hashtags:
            users = sender.user_handler.find_users_by_hashtag(hashtag, max_users=5)
            all_users.update(users)
            time.sleep(random.uniform(20, 40))  # Longer delay between hashtags
        
        users = list(all_users)
        if not users:
            print("[ERROR] No users found")
            return
        
        # Randomize user order
        random.shuffle(users)
        print(f"Found {len(users)} total users (randomized)")
        
        # Filter out users who already received messages
        filtered_users = [
            user for user in users 
            if not sender.history_manager.has_shared_with_user(user, "promo_message")
        ]
        
        print(f"\n[STEP 2] Sending messages to {len(filtered_users)} users")
        successful_users = []
        
        for index, username in enumerate(filtered_users, 1):
            print(f"\nProcessing user {index}/{len(filtered_users)}: {username}")
            
            if sender.send_promotional_message(username):
                successful_users.append(username)
                sender.history_manager.update_history(username, "promo_message")
                
                # Random delay between messages (longer to avoid spam detection)
                delay = random.uniform(40, 600)
                print(f"Waiting {delay:.1f} seconds before next message...")
                time.sleep(delay)
        
        print(f"\nCompleted! Successfully sent messages to {len(successful_users)} users")
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
