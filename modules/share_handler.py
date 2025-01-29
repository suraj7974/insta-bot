from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time

class ShareHandler:
    def __init__(self, driver):
        self.driver = driver

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
