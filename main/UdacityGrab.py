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

import zipfile

class UdacityCourseDownloader:
    def __init__(self, email, password):
        self.email = email
        self.password = password
                
        self.video_urls = []
        self.download_path = "downloaded_videos"

        self.driver = self._init_driver()
        self.sublessons_urls = []
        self.current_video_num = 1

        os.makedirs(self.download_path, exist_ok=True)
        
    def _init_driver(self):
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
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        # Enhanced stealth settings
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        })
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        return driver 

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
                                time.sleep(0.5)
                                break
                        except:
                            continue
                except Exception as e:
                    print(f"Error finding sign-in link: {str(e)}")
                    # Try direct navigation as fallback
                    self.driver.get("https://auth.udacity.com/sign-in")
                    time.sleep(0.5)
            
            # Wait for page load and check URL
            time.sleep(0.5)
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
                            print("Successfully redirected to Course Page")
                            return True
                        elif "sign-up" in current_url:
                            print("Redirected to sign-up page, login failed")
                            return False
                        time.sleep(1)

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

    def navigate_to_course(self, course_url):
        """Navigate directly to course using URL"""
        try:
            self.driver.get(course_url)
            
            # First check for and click resume/start button
            try:
                resume_buttons = [
                    "//button[.//*[contains(text(), 'Resume')]]",
                    "//button[contains(., 'Start Learning')]",
                    "//a[contains(., 'Resume')]",
                    "//a[contains(., 'Start Learning')]"
                ]
                
                for selector in resume_buttons:
                    try:
                        button = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        if button:
                            print("Found resume/start button, clicking...")
                            self.driver.execute_script("arguments[0].click();", button)
                            # Wait for lessons to load
                            WebDriverWait(self.driver, 20).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='course-curriculum']"))
                            )
                            return True
                    except:
                        continue
            except Exception as e:
                print(f"Resume button handling error: {str(e)}")

            # Fallback to original curriculum check
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='course-curriculum']"))
                )
                return True
            except:
                print("Failed to find curriculum section")
                return False

        except Exception as e:
            print(f"Course navigation failed: {str(e)}")
            return False
        
    def _expand_all_sections(self):
        try:
            max_retries = 3
            for _ in range(max_retries):
                expand_buttons = self.driver.find_elements(
                    By.XPATH, "//button[contains(@aria-label, 'Expand') or contains(@aria-label, 'Collapse')]"
                )
                for btn in expand_buttons:
                    try:
                        if "Expand" in btn.get_attribute("aria-label"):
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                            btn.click()
                            time.sleep(0.3)
                    except:
                        continue
                time.sleep(1)
        except Exception as e:
            print(f"Section expansion error: {str(e)}")

    def collect_sublessons_urls(self):
        try:
            self._expand_all_sections()
            time.sleep(1)
            
            # Get all lesson links including those in nested lists
            sublesson_links = WebDriverWait(self.driver, 20).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//div[@data-testid='course-curriculum']//a[contains(@href, '/lessons/')]")
                )
            )
            
            # Filter unique URLs maintaining order
            seen = set()
            self.sublesson_urls = []
            for link in sublesson_links:
                url = link.get_attribute("href")
                if url not in seen:
                    seen.add(url)
                    self.sublesson_urls.append(url)
            
            print(f"Found {len(self.sublesson_urls)} sub-lessons")
            return True
        except Exception as e:
            print(f"Sublesson collection error: {str(e)}")
            return False
        
    def _get_zip_url(self):
        try:

            #Switch to Downloads tab
            downloads_tab = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Downloads')]"))
            )
            downloads_tab.click()
            time.sleep(1)

            # Get zip URL
            zip_link = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '.zip') and contains(text(), 'Videos')]"))
            )
            return zip_link.get_attribute("href")

        except Exception as e:
            print (f"Downlod tab error: {e}")
            return None

    def _download_and_extract_zip(self, zip_url):
        try: 
            #use session cookies for authentication

            session = requests.Session()
            for cookie in self.driver.get_cookies():
                session.cookies.set(cookie['name'], cookie['value'])
            response = session.get(zip_url, stream=True)
            zip_path = os.path.join(self.download_path, f"temp_{self.current_video_num}")

            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size = 128):
                    f.write(chunk)

            #Extract video
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for file in zip_ref.namelist():
                    if file.endswith('.mp4'):
                        zip_ref.extract(file, self.download_path)
                        os.rename(
                            os.path.join(self.download_path, file),
                            os.path.join(self.download_path, f"video_{self.current_video_num}.mp4")
                        )
                        break
                    
            os.remove(zip_path)  # Cleanup zip
            self.current_video_num += 1
            return True

                
        except Exception as e:
            print(f"Download error : {e}")
            return False
        
    def process_sublessons(self):
        for url in self.sublesson_urls:
            print(f"Processing: {url}")
            self.driver.get(url)
            time.sleep(2)
            
            zip_url = self._get_zip_url()
            if zip_url:
                self._download_and_extract_zip(zip_url)


    # def collect_video_urls(self):
    #     try:
    #         # Expand all lessons first
    #         expand_buttons = self.driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'Expand')]")
    #         for btn in expand_buttons:
    #             self.driver.execute_script("arguments[0].scrollIntoView();", btn)
    #             btn.click()
    #             time.sleep(1)

    #         # Find video links
    #         video_links = WebDriverWait(self.driver, 20).until(
    #             EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='/videos/']"))
    #         )
            
    #         self.video_urls = [link.get_attribute("href") for link in video_links]
    #         print(f"Found {len(self.video_urls)} video links")
    #         return True
            
    #     except Exception as e:
    #         print(f"Failed to collect video URLs: {str(e)}")
    #         return False

    # def download_videos(self):
    #     for i, url in enumerate(self.video_urls):
    #         try:
    #             # Navigate to video page
    #             self.driver.get(url)
    #             time.sleep(3)
                
    #             # Find video source
    #             video_element = WebDriverWait(self.driver, 10).until(
    #                 EC.presence_of_element_located((By.TAG_NAME, "video"))
    #             )
    #             video_url = video_element.get_attribute("src")
                
    #             # Download video
    #             response = requests.get(video_url, stream=True)
    #             video_path = os.path.join(self.download_path, f"video_{i+1}.mp4")
                
    #             with open(video_path, "wb") as f:
    #                 for chunk in response.iter_content(chunk_size=1024):
    #                     if chunk:
    #                         f.write(chunk)
                
    #             print(f"Downloaded video {i+1}/{len(self.video_urls)}")
    #         except Exception as e:
    #             print(f"Failed to download video {i+1}: {str(e)}")
 
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
    # Get credentials and course URL from environment variables
    email = os.getenv('UDACITY_EMAIL')
    password = os.getenv('UDACITY_PASSWORD')
    course_url = os.getenv('UDACITY_COURSE_URL')  # Changed from course_name to course_url
    
    if not all([email, password, course_url]):
        print("Please set UDACITY_EMAIL, UDACITY_PASSWORD, and UDACITY_COURSE_URL environment variables")
        return
    
    downloader = UdacityCourseDownloader(email, password)
    
    if downloader.login():
        if downloader.navigate_to_course(course_url):  # Now using course_url
            if downloader.collect_video_urls():
                downloader.download_videos()
                downloader.concatenate_videos()
    
    downloader.cleanup()

if __name__ == "__main__":
    main()


