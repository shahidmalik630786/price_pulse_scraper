import csv
import os
import time
import json
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import undetected_chromedriver as uc


# ---------------------- Configuration -----------------------
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
]

PROXIES = [
    # "http://user:pass@proxy1:port",
]

# ---------------------- Utilities -----------------------
def get_random_proxy():
    return random.choice(PROXIES) if PROXIES else None


def init_stealth_driver():
    options = uc.ChromeOptions()
    
    # Enhanced stealth settings
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-extensions")
    options.add_argument("--dns-prefetch-disable")
    
    # Remove headless mode for better Cloudflare bypass
    # options.add_argument("--headless=new")  # Keep commented for visibility

    user_agent = random.choice(USER_AGENTS)
    options.add_argument(f"user-agent={user_agent}")

    proxy = get_random_proxy()
    if proxy:
        options.add_argument(f'--proxy-server={proxy}')

    options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_settings.popups": 0,
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False
    })

    # Initialize driver - Let undetected_chromedriver auto-manage everything
    try:
        # Don't specify driver_executable_path - let UC handle it
        driver = uc.Chrome(
            options=options,
            use_subprocess=False,
            version_main=141  # Match your Chrome version
        )
        print("✓ Driver initialized successfully")
    except Exception as e:
        print(f"Initialization with version_main failed: {e}")
        try:
            # Try without version specification
            driver = uc.Chrome(
                options=options,
                use_subprocess=False
            )
            print("✓ Driver initialized with auto-detection")
        except Exception as e2:
            print(f"Auto-detection failed: {e2}")
            # Last resort - minimal options
            driver = uc.Chrome(use_subprocess=False)
            print("✓ Driver initialized with minimal options")
    
    # Set longer timeout for Cloudflare checks
    driver.set_page_load_timeout(120)
    
    # Execute CDP commands to further hide automation (if supported)
    try:
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": user_agent,
            "platform": "Win32",
            "acceptLanguage": "en-US,en;q=0.9"
        })
    except:
        pass
    
    try:
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    except:
        pass
    
    return driver


def wait_for_cloudflare(driver, timeout=30):
    """Wait for Cloudflare challenge to complete"""
    print("Checking for Cloudflare challenge...")
    
    try:
        # Wait for Cloudflare challenge to disappear
        WebDriverWait(driver, timeout).until_not(
            EC.presence_of_element_located((By.ID, "challenge-running"))
        )
        time.sleep(2)
        
        # Check if we're still on a challenge page
        if "challenge" in driver.current_url.lower() or \
           "ray id" in driver.page_source.lower():
            print("Cloudflare challenge detected, waiting...")
            time.sleep(random.uniform(8, 15))
        
        # Additional wait for page to fully load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        return True
    except TimeoutException:
        print("Cloudflare bypass may have failed or took too long")
        return False
    except Exception as e:
        print(f"Error during Cloudflare check: {e}")
        return False


def to_csv(username, email, phonenumber, password1, address, latitude, longitude, provider_type, provider_name, state, city_name):
    filename = f"{state}_{city_name}_{provider_type}.csv".replace(" ", "_").lower()
    folder = "Georgia/alpharetta"
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)

    file_exists = os.path.isfile(filepath)
    with open(filepath, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow([
                'Username', 'Email', 'Phone Number', 'Password',
                'Address', 'Latitude', 'Longitude',
                'Provider Type', 'Provider Name',
                'State', 'City'
            ])
        writer.writerow([
            username, email, phonenumber, password1,
            address, latitude, longitude,
            provider_type, provider_name,
            state, city_name
        ])


def read_urls_from_csv(state, city_name, provider_type):
    filename = f"{state}_{city_name}_{provider_type}_urls.csv".replace(" ", "_").lower()
    filepath = os.path.join("Georgia/alpharetta", filename)
    urls = []
    if os.path.exists(filepath):
        with open(filepath, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                urls.append(row['Url'] if 'Url' in row else list(row.values())[0])
    else:
        print(f"URL CSV file not found: {filepath}")
    return urls


def scrape_url(urls, driver, key, state, city_name):
    url_count = 1
    last_init_time = time.time()
    failed_urls = []

    for url in urls:
        print(f"\n{'='*60}")
        print(f"url_count: {url_count}/{len(urls)} - Scraping: {url}")
        print(f"{'='*60}")

        # Re-initialize driver after 10 minutes
        if time.time() - last_init_time >= 600:
            print("10 minutes elapsed, reinitializing driver...")
            try:
                driver.quit()
            except:
                pass
            time.sleep(random.uniform(3, 7))
            driver = init_stealth_driver()
            last_init_time = time.time()

        max_retries = 3
        retry_count = 0
        success = False

        while retry_count < max_retries and not success:
            try:
                # Random delay between requests
                if url_count > 1:
                    delay = random.uniform(3, 8)
                    print(f"Waiting {delay:.2f} seconds before next request...")
                    time.sleep(delay)

                print(f"Attempt {retry_count + 1}/{max_retries}")
                driver.get(url)
                
                # Wait for Cloudflare challenge
                if not wait_for_cloudflare(driver):
                    raise Exception("Cloudflare challenge not resolved")
                
                # Additional random human-like delay
                time.sleep(random.uniform(2, 4))

                # Try to find elements with explicit waits
                wait = WebDriverWait(driver, 15)
                
                username_element = wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'sales-info'))
                )
                username = username_element.text.strip()

                details = wait.until(
                    EC.presence_of_element_located((By.ID, 'default-ctas'))
                )
                phonenumber = details.find_element(By.CLASS_NAME, 'phone').text.strip()
                address = details.find_element(By.CLASS_NAME, 'address').text.strip()

                script_tag = wait.until(
                    EC.presence_of_element_located((By.XPATH, '//script[@type="application/ld+json"]'))
                )
                json_content = script_tag.get_attribute('innerHTML')
                data = json.loads(json_content)

                username_parts = username.split()
                email = "".join(username_parts) + "@gmail.com"
                password1 = username_parts[0] + "@123" if username_parts else "default@123"
                provider_name = username
                latitude = data.get('geo', {}).get('latitude')
                longitude = data.get('geo', {}).get('longitude')

                to_csv(username, email, phonenumber, password1, address, latitude, 
                       longitude, key, provider_name, state, city_name)
                
                print(f"✓ Successfully scraped: {username}")
                success = True

            except TimeoutException as e:
                retry_count += 1
                print(f"✗ Timeout error (attempt {retry_count}/{max_retries}): {e}")
                if retry_count < max_retries:
                    wait_time = random.uniform(5, 10) * retry_count
                    print(f"Waiting {wait_time:.2f} seconds before retry...")
                    time.sleep(wait_time)
                    
            except WebDriverException as e:
                retry_count += 1
                print(f"✗ WebDriver error (attempt {retry_count}/{max_retries}): {e}")
                if retry_count < max_retries:
                    # Reinitialize driver on WebDriver errors
                    try:
                        driver.quit()
                    except:
                        pass
                    time.sleep(random.uniform(5, 10))
                    driver = init_stealth_driver()
                    last_init_time = time.time()
                    
            except Exception as e:
                retry_count += 1
                print(f"✗ Error (attempt {retry_count}/{max_retries}): {e}")
                if retry_count < max_retries:
                    time.sleep(random.uniform(3, 7))

        if not success:
            print(f"✗ Failed to scrape after {max_retries} attempts: {url}")
            failed_urls.append(url)

        url_count += 1

    # Save failed URLs for retry
    if failed_urls:
        failed_filename = f"{state}_{city_name}_{key}_failed.csv".replace(" ", "_").lower()
        failed_filepath = os.path.join("Georgia/alpharetta", failed_filename)
        with open(failed_filepath, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Url'])
            for failed_url in failed_urls:
                writer.writerow([failed_url])
        print(f"\n{len(failed_urls)} failed URLs saved to: {failed_filepath}")

    return driver


# ---------------------- Script Entry -----------------------
if __name__ == "__main__":
    state = "ga"
    city_name = "alpharetta"
    key = "chiropractics"

    urls = read_urls_from_csv(state, city_name, key)

    if urls:
        print(f"Total URLs to scrape: {len(urls)}")
        print("Starting scraper with Cloudflare bypass...")
        
        driver = None
        try:
            driver = init_stealth_driver()
            driver = scrape_url(urls, driver, key, state, city_name)
        except KeyboardInterrupt:
            print("\nScraping interrupted by user")
        except Exception as e:
            print(f"Fatal error: {e}")
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
            print("\nScraping completed!")
    else:
        print("No URLs found to scrape.")