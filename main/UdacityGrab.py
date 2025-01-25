from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import os
from moviepy.editor import VideoFileClip, concatenate_videoclips
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class UdacityCourseDownloader:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        
        # Enhanced Chrome options for better stealth
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument(f'--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
        
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Initialize driver with options
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        # Enhanced stealth settings
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        })
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.video_urls = []
        self.download_path = "downloaded_videos"
        
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)

    def login(self):
        try:
            # Start with sign-in URL directly
            self.driver.get("https://auth.udacity.com/sign-in")
            print("Navigating to login page...")
            
            # If redirected to sign-up, click the sign-in link
            if "sign-up" in self.driver.current_url:
                try:
                    sign_in_link_selectors = [
                        "a[href*='sign-in']",
                        "a.auth-link",
                        "//a[contains(text(), 'Sign In')]",
                        "//a[contains(text(), 'Already have an account?')]"
                    ]
                    
                    for selector in sign_in_link_selectors:
                        try:
                            if selector.startswith("//"):
                                sign_in_link = WebDriverWait(self.driver, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, selector))
                                )
                            else:
                                sign_in_link = WebDriverWait(self.driver, 5).until(
                                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                                )
                            if sign_in_link:
                                print("Found sign in link, clicking...")
                                self.driver.execute_script("arguments[0].click();", sign_in_link)
                                time.sleep(5)
                                break
                        except:
                            continue
                except Exception as e:
                    print(f"Error finding sign-in link: {str(e)}")
                    # Try direct navigation as fallback
                    self.driver.get("https://auth.udacity.com/sign-in")
                    time.sleep(5)
            
            # Wait for page load and check URL
            time.sleep(5)
            current_url = self.driver.current_url
            print(f"Current URL: {current_url}")
            
            try:
                # Wait for email field with multiple possible selectors
                email_field = None
                possible_email_selectors = [
                    "input[aria-label='Email Address']",
                    "input[type='email']",
                    "input[name='email']",
                    "#email"
                ]
                
                for selector in possible_email_selectors:
                    try:
                        email_field = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        if email_field:
                            break
                    except:
                        continue
                
                if not email_field:
                    raise Exception("Could not find email field")
                
                # Clear and enter email with delay
                email_field.clear()
                for char in self.email:
                    email_field.send_keys(char)
                    time.sleep(0.1)
                print("Entered email.")
                
                # Similar approach for password field
                password_field = None
                possible_password_selectors = [
                    "input[aria-label='Password']",
                    "input[type='password']",
                    "input[name='password']",
                    "#password"
                ]
                
                for selector in possible_password_selectors:
                    try:
                        password_field = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        if password_field:
                            break
                    except:
                        continue
                
                if not password_field:
                    raise Exception("Could not find password field")
                
                # Clear and enter password with delay
                password_field.clear()
                for char in self.password:
                    password_field.send_keys(char)
                    time.sleep(0.1)
                print("Entered password.")
                
                # Updated button selection for the blue Sign in button
                sign_in_button = None
                try:
                    # Look specifically for the blue button in the center
                    button_selectors = [
                        "button.button--primary[type='submit']",  # Primary class usually indicates main CTA
                        "button.sign-in-button[type='submit']",
                        "button.primary-button[type='submit']",
                        "//button[@type='submit' and contains(@class, 'primary')]",
                        "//button[contains(@class, 'button--primary')]",
                        # The specific button in the form
                        "form button[type='submit']",
                        # Look for the button with arrow icon
                        "button.button--primary svg"
                    ]
                    
                    for selector in button_selectors:
                        try:
                            if selector.startswith("//"):
                                sign_in_button = WebDriverWait(self.driver, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, selector))
                                )
                            else:
                                sign_in_button = WebDriverWait(self.driver, 5).until(
                                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                                )
                            if sign_in_button:
                                print(f"Found primary sign in button using selector: {selector}")
                                break
                        except:
                            continue

                    if not sign_in_button:
                        # Fallback: Find all buttons and look for the one with the right styling
                        buttons = self.driver.find_elements(By.TAG_NAME, "button")
                        for button in buttons:
                            try:
                                classes = button.get_attribute("class")
                                if ("primary" in classes.lower() and 
                                    "submit" in button.get_attribute("type").lower()):
                                    sign_in_button = button
                                    print("Found sign in button through class analysis")
                                    break
                            except:
                                continue

                    if not sign_in_button:
                        raise Exception("Could not find the primary sign in button")

                    # Click the button and wait for navigation
                    self.driver.execute_script("arguments[0].click();", sign_in_button)
                    print("Clicked primary sign in button")

                    # Wait for dashboard redirect
                    dashboard_url = "https://www.udacity.com/dashboard"
                    max_wait = 30
                    start_time = time.time()
                    
                    while time.time() - start_time < max_wait:
                        current_url = self.driver.current_url
                        if dashboard_url in current_url:
                            print("Successfully redirected to dashboard")
                            return True
                        elif "sign-up" in current_url:
                            print("Redirected to sign-up page, login failed")
                            return False
                        time.sleep(2)

                    print("Timed out waiting for dashboard redirect")
                    return False

                except Exception as e:
                    print(f"Error clicking sign in button: {str(e)}")
                    self.driver.save_screenshot(f"login_error_{time.time()}.png")
                    return False
                
            except Exception as inner_e:
                print(f"Error during login process: {str(inner_e)}")
                self.driver.save_screenshot(f"login_error_{time.time()}.png")
                return False
                
        except Exception as e:
            print(f"Login failed: {str(e)}")
            self.driver.save_screenshot(f"login_error_outer_{time.time()}.png")
            return False

    def navigate_to_course(self, course_name):
        try:
            # First try the dashboard
            self.driver.get("https://learn.udacity.com/my-programs")
            print("Navigating to programs page...")
            time.sleep(5)

            # If redirected to dashboard, try to find "My Programs" or similar navigation
            dashboard_nav_selectors = [
                "a[href*='my-programs']",
                "a[href*='courses']",
                "//a[contains(text(), 'My Programs')]",
                "//a[contains(text(), 'Courses')]",
                "//span[contains(text(), 'My Programs')]/..",
                "//span[contains(text(), 'Courses')]/.."
            ]

            for selector in dashboard_nav_selectors:
                try:
                    if selector.startswith("//"):
                        nav_element = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        nav_element = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    if nav_element:
                        print("Found navigation element, clicking...")
                        self.driver.execute_script("arguments[0].click();", nav_element)
                        time.sleep(3)
                        break
                except:
                    continue

            # Try to find and click the search icon/button
            search_button_selectors = [
                "button[aria-label*='search' i]",  # 'i' flag for case-insensitive
                "button[title*='search' i]",
                ".search-icon",
                "//button[contains(translate(@aria-label, 'SEARCH', 'search'), 'search')]",
                "//button[contains(@class, 'search')]",
                "//i[contains(@class, 'search')]/.."
            ]

            print("Looking for search button...")
            for selector in search_button_selectors:
                try:
                    if selector.startswith("//"):
                        search_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        search_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    if search_button:
                        print("Found search button, clicking...")
                        self.driver.execute_script("arguments[0].click();", search_button)
                        time.sleep(2)
                        break
                except:
                    continue

            # Try to find the search box
            search_selectors = [
                "input[placeholder*='search' i]",
                "input[type='search']",
                "input[aria-label*='search' i]",
                "//input[contains(@placeholder, 'Search')]",
                "//input[@type='search']"
            ]

            print("Looking for search input...")
            for selector in search_selectors:
                try:
                    if selector.startswith("//"):
                        search_box = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, selector))
                        )
                    else:
                        search_box = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                    if search_box:
                        print(f"Found search box, entering course name: {course_name}")
                        search_box.clear()
                        # Type the course name with a small delay
                        for char in course_name:
                            search_box.send_keys(char)
                            time.sleep(0.1)
                        time.sleep(2)
                        break
                except:
                    continue

            # Look for the course in search results
            course_selectors = [
                f"//div[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{course_name.lower()}')]",
                f"//h3[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{course_name.lower()}')]",
                f"//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{course_name.lower()}')]",
                ".course-card",
                ".nanodegree-card",
                "//div[contains(@class, 'card')]"
            ]

            print("Looking for course in search results...")
            for selector in course_selectors:
                try:
                    if selector.startswith("//"):
                        course_element = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        course_element = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    if course_element:
                        print("Found course element, clicking...")
                        # Scroll the element into view
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", course_element)
                        time.sleep(1)
                        self.driver.execute_script("arguments[0].click();", course_element)
                        time.sleep(5)
                        return True
                except:
                    continue

            print("Could not find course through search")
            return False

        except Exception as e:
            print(f"Navigation failed: {str(e)}")
            self.driver.save_screenshot(f"course_search_error_{time.time()}.png")
            return False

    def collect_video_urls(self):
        try:
            # Find all chapter sections
            chapters = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".lesson-list"))
            )
            
            for chapter in chapters:
                # Find all video links in the chapter
                video_elements = chapter.find_elements(By.CSS_SELECTOR, "a[href*='video']")
                for video_element in video_elements:
                    self.video_urls.append(video_element.get_attribute("href"))
            
            return True
        except Exception as e:
            print(f"Failed to collect video URLs: {str(e)}")
            return False

    def download_videos(self):
        for i, url in enumerate(self.video_urls):
            try:
                # Navigate to video page
                self.driver.get(url)
                time.sleep(3)
                
                # Find video source
                video_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "video"))
                )
                video_url = video_element.get_attribute("src")
                
                # Download video
                response = requests.get(video_url, stream=True)
                video_path = os.path.join(self.download_path, f"video_{i+1}.mp4")
                
                with open(video_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                
                print(f"Downloaded video {i+1}/{len(self.video_urls)}")
            except Exception as e:
                print(f"Failed to download video {i+1}: {str(e)}")

    def concatenate_videos(self, output_filename="final_video.mp4"):
        try:
            video_files = sorted([f for f in os.listdir(self.download_path) if f.endswith('.mp4')])
            clips = [VideoFileClip(os.path.join(self.download_path, f)) for f in video_files]
            
            final_clip = concatenate_videoclips(clips)
            final_clip.write_videofile(output_filename)
            
            # Clean up clips
            for clip in clips:
                clip.close()
            
            return True
        except Exception as e:
            print(f"Failed to concatenate videos: {str(e)}")
            return False

    def cleanup(self):
        self.driver.quit()

def main():
    # Replace with your credentials and course URL
    email = "email"
    password = "password"
    course_name = "course_name"  # Use the actual course name
    
    downloader = UdacityCourseDownloader(email, password)
    
    if downloader.login():
        if downloader.navigate_to_course(course_name):
            if downloader.collect_video_urls():
                downloader.download_videos()
                downloader.concatenate_videos()
    
    downloader.cleanup()

if __name__ == "__main__":
    main()


#git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch D:\OneDrive - aucegypt.edu\Desktop\CS221 Stanford\classwork\UDACITY.py' --prune-empty --tag-name-filter cat -- --all
