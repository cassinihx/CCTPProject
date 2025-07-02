import sys, os, time, random
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

URL = "https://pimeyes.com/en"

def human_like_delay(min_time=1.5, max_time=3.5):
    time.sleep(random.uniform(min_time, max_time))

def move_mouse_and_click(driver, element):
    """Moves the mouse to the element before clicking to mimic human interaction."""
    action = ActionChains(driver)
    action.move_to_element(element).pause(random.uniform(1, 2)).click().perform()

def upload(url, image_path):
    driver = None

    # Resolve absolute path
    image_path = os.path.abspath(image_path.strip())

    # Check if file exists
    if not os.path.isfile(image_path):
        print(f"Error: File not found at '{image_path}'. Please check the path and try again.")
        return
    else:
        print(f"Image found: {image_path}")

    try:
        # Start Selenium without headless mode
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Prevent detection
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)

        # Ensure the page is fully loaded
        print("Waiting for the page to load...")
        human_like_delay(4, 6)

        # Accept cookies if prompted
        try:
            print("Checking for cookie popup...")
            cookie_popup = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="CybotCookiebotDialog"]'))
            )
            accept_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"]'))
            )
            move_mouse_and_click(driver, accept_button)
            print("Cookies accepted!")
            human_like_delay(2, 4)
        except:
            print("No cookie popup detected. Continuing...")

        # Click the "Upload Photos" button first
        try:
            print("Searching for the 'Upload Photos' button...")
            upload_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="hero-section"]/div/div[1]/div/div/div[1]/button[2]'))
            )
            move_mouse_and_click(driver, upload_button)
            print("'Upload Photos' button clicked!")
        except:
            print("'Upload Photos' button not found.")
            driver.quit()
            return

        human_like_delay(2, 4)  # Allow upload window to open

        # ✅ Find the hidden file input and upload the image
        try:
            print("Searching for the hidden file input...")
            file_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "file-input"))
            )
            print("File input found! Uploading image...")
            file_input.send_keys(image_path)
            print("Image uploaded successfully!")
        except:
            print("File input field not found.")
            driver.quit()
            return

        human_like_delay(3, 5)  # Allow UI to process the upload

        # Extra wait before checking checkboxes
        print("Waiting before checking checkboxes to prevent bot detection...")
        human_like_delay(4, 6)

        # Locate checkboxes dynamically
        try:
            print("Searching for checkboxes...")
            checkboxes = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input[type='checkbox'][required]"))
            )

            if len(checkboxes) >= 3:
                for index, checkbox in enumerate(checkboxes[:3]):
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", checkbox)
                    human_like_delay(1, 2)  # Pause before clicking
                    move_mouse_and_click(driver, checkbox)  # Mimic real clicking
                    human_like_delay(2, 4)
                    print(f"Checkbox {index + 1} ticked!")
            else:
                print(f"⚠ Expected 3 checkboxes, but found {len(checkboxes)}.")
                driver.quit()
                return
        except:
            print("Checkboxes not found.")
            driver.quit()
            return

        # Locate and Click the "Start Search" Button
        try:
            print("Searching for the 'Start Search' button...")

            # Find the button by its text (works even if the class changes)
            start_search_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Start Search']]"))
            )

            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", start_search_button)
            human_like_delay(3, 5)  # Extra wait to prevent bot detection
            move_mouse_and_click(driver, start_search_button)
            print("Search started successfully!")

        except:
            print("'Start Search' button not found.")
            driver.quit()
            return

        human_like_delay(12, 15)  # Allow PimEyes to process the search

        # Capture results page URL
        search_results_url = driver.current_url
        print("Search Results URL:", search_results_url)

    except Exception as e:
        print(f"❌ An error occurred: {e}")

    finally:
        if driver:
            driver.quit()

def main():
    # NEW: allow  path via CLI   ->  python main.py <image_path>
    if len(sys.argv) >= 2:
        image_path = sys.argv[1]
    else:
        image_path = input("Enter the path to the image: ").strip()

    # strip quotes
    if image_path.startswith(("\"", "'")) and image_path.endswith(("\"", "'")):
        image_path = image_path[1:-1]

    upload(URL, image_path)


if __name__ == "__main__":
    main()