import random
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import json
# from accounts.models import CustomUser, UserProfile
# from provider.models import ProviderType, Address, Provider
# from django.contrib.gis.geos import Point
# from django.template.defaultfilters import slugify
# from core.models import Service
from selenium.common.exceptions import TimeoutException
import csv
import os


# def insert_to_database(username, email, phonenumber, password1, address, latitude, longitude, role, provider_type, provider_name):
#     print(f"Username: {username}, Email: {email}, Phonenumber: {phonenumber}, Password: {password1}, Latitude: {latitude}, Longitude: {longitude}")
#     user, created = CustomUser.objects.get_or_create(
#         username=username,
#         defaults={
#             'email': email,
#             'phonenumber': phonenumber,
#             'role': role,
#             'is_active': True,
#         }
#     )

#     if created:
#         user.set_password(password1)
#         user.save()
#         print(f"User: {username} created successfully")

#         # Create address instance
#         address_obj = Address.objects.create(
#             user=user,
#             address=address,
#             latitude=str(latitude),
#             longitude=str(longitude),
#             location=Point(longitude, latitude)
#         )

#         # Create UserProfile
#         user_profile, _ = UserProfile.objects.get_or_create(user=user)

#         # Create Provider instance
#         provider = Provider.objects.create(
#             user=user,
#             profile=user_profile,
#             address=address_obj,
#             provider_type=provider_type,
#             provider_name=provider_name,
#             provider_slug=slugify(provider_name),
#             location=Point(longitude, latitude),
#         )
#         provider.services.add(*Service.objects.filter(category='IMAGING'))
#     else:
#         print(f"User: {username} Already Exists")



def to_csv(username, email, phonenumber, password1, address, latitude, longitude, provider_type, provider_name, state, city_name):
    # Clean and prepare filename
    filename = f"{state}_{city_name}_{provider_type}.csv".replace(" ", "_").lower()
    folder = "Georgia"
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)

    # Check if file already exists to write header only once
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


def urls_to_csv(urls, state, city_name, provider_type):
    # Clean and prepare filename
    filename = f"{state}_{city_name}_{provider_type}_urls.csv".replace(" ", "_").lower()
    folder = "Georgia"
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)

    # Check if file already exists to write header only once
    file_exists = os.path.isfile(filepath)

    with open(filepath, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(['Url'])

        for url in urls:
            writer.writerow([url])



def scrape_url(urls, driver, key, last_init_time, state, city_name):
    url_count = 1
    for url in urls:
        print(f"url_count: {url_count}")
        # Check if 10 minutes have passed since last driver initialization
        if time.time() - last_init_time >= 600:  # 600 seconds = 10 minutes
            print("10 minutes elapsed, reinitializing driver...")
            try:
                driver.quit()
            except:
                pass
            driver = init_stealth_driver()
            last_init_time = time.time()
        try:
            time.sleep(1)
            driver.get(f"{url}")
            time.sleep(3)
            username_element = driver.find_element(By.CLASS_NAME, 'sales-info')
            username = username_element.text
            details = driver.find_element(By.ID, 'default-ctas')
            phonenumber_element = details.find_element(By.CLASS_NAME, 'phone')
            phonenumber = phonenumber_element.text
            address_element = details.find_element(By.CLASS_NAME, 'address')
            address = address_element.text
            script_tag = driver.find_element(By.XPATH, '//script[@type="application/ld+json"]')
            json_content = script_tag.get_attribute('innerHTML')
            data = json.loads(json_content)

            username_len = len(username.split(' '))
            if username_len > 1:
                name_str = username.split(' ')[0]
                last_str = username.split(' ')[1]
                email = name_str + last_str + "@gmail.com"
            elif username_len > 2:
                name_str = username.split(' ')[0]
                last_str = username.split(' ')[1]
                last_str2 = username.split(' ')[2]
                email = name_str + last_str + last_str2 + "@gmail.com"
            else:
                name_str = username
                email = name_str + "@gmail.com"

            password1 = name_str + "@123"
            provider_name = username
            # role = CustomUser.PROVIDER
            # provider_type = ProviderType.objects.get(code=key)
            latitude = data.get('geo', {}).get('latitude')
            longitude = data.get('geo', {}).get('longitude')

            # insert_to_database(username, email, phonenumber, password1, address, latitude, longitude, role, provider_type, provider_name)

            to_csv(username, email, phonenumber, password1, address, latitude, longitude, key, provider_name, state, city_name)
            
        except Exception as e:
            print(f"Error processing URL {url}: {str(e)}")
        
        url_count += 1
    return driver, last_init_time


def remove_interfering_elements(driver):
    """Remove ads and overlays that interfere with clicking"""
    try:
        driver.execute_script("""
            // Remove Google ads and other iframes
            var ads = document.querySelectorAll('iframe[id*="google_ads"], iframe[src*="googlesyndication"], iframe[src*="safeframe"]');
            ads.forEach(function(ad) { 
                ad.style.display = 'none';
                ad.remove();
            });
            
            // Remove overlay elements
            var overlays = document.querySelectorAll('[class*="overlay"], [class*="popup"], [class*="modal"]');
            overlays.forEach(function(overlay) { 
                overlay.style.display = 'none'; 
            });
            
            // Remove fixed positioned elements with high z-index
            var fixedElements = document.querySelectorAll('*');
            fixedElements.forEach(function(el) {
                var style = window.getComputedStyle(el);
                if (style.position === 'fixed' && parseInt(style.zIndex) > 1000) {
                    el.style.display = 'none';
                }
            });
        """)
    except Exception as e:
        print(f"Error removing interfering elements: {e}")


def robust_click(driver, element):
    """Try multiple click strategies"""
    strategies = [
        # Strategy 1: Standard click after scroll
        lambda: [
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element),
            time.sleep(1),
            element.click()
        ],
        
        # Strategy 2: JavaScript click
        lambda: driver.execute_script("arguments[0].click();", element),
        
        # Strategy 3: Dispatch click event
        lambda: driver.execute_script("""
            var event = new MouseEvent('click', {
                view: window,
                bubbles: true,
                cancelable: true
            });
            arguments[0].dispatchEvent(event);
        """, element),
        
        # Strategy 4: Focus and click
        lambda: [
            driver.execute_script("arguments[0].focus();", element),
            element.click()
        ]
    ]
    
    for i, strategy in enumerate(strategies, 1):
        try:
            print(f"Trying click strategy {i}")
            if callable(strategy):
                strategy()
            else:
                for action in strategy:
                    action()
            return True
        except Exception as e:
            print(f"Strategy {i} failed: {str(e)[:50]}...")
            continue
    
    return False


def navigate_by_url(driver, base_url, page_num):
    """Fallback navigation by URL manipulation"""
    try:
        current_url = driver.current_url
        
        if 'page=' in current_url:
            import re
            new_url = re.sub(r'page=\d+', f'page={page_num}', current_url)
        else:
            separator = '&' if '?' in current_url else '?'
            new_url = f"{current_url}{separator}page={page_num}"
        
        print(f"Navigating via URL to page {page_num}")
        driver.get(new_url)
        time.sleep(3)
        return True
    except Exception as e:
        print(f"URL navigation failed: {e}")
        return False


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
]


PROXIES = [
    # "http://user:pass@proxy1:port",
    # "http://user:pass@proxy2:port",
]


def get_random_proxy():
    if PROXIES:
        return random.choice(PROXIES)
    return None


def init_stealth_driver():
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    user_agent = random.choice(USER_AGENTS)
    options.add_argument(f"user-agent={user_agent}")
    proxy = get_random_proxy()
    if proxy:
        options.add_argument(f'--proxy-server={proxy}')
    options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_settings.popups": 0,
        "profile.managed_default_content_settings.images": 2
    })
    driver = uc.Chrome(driver_executable_path='/home/shahid/bin/chromedriver', options=options, headless=False)

    driver.set_page_load_timeout(90)
    return driver


def scrape_yellow_pages():
    print("SCRAPPING STARTED.....")
    driver = init_stealth_driver()
    last_init_time = time.time()  # Initialize the time tracking
    driver.get("https://www.yellowpages.com/sitemap")
    driver.maximize_window()
    time.sleep(3)

    # states = ["ak", "al", "ar", "az", "ca", "co", "ct", "de", "fl", "ga", "hi", "ia", "id", "il", "in", "ks", "ky", "la", "ma", "md", 
    #           "me", "mi", "mn", "mo", "ms", "mt", "nc", "nd", "ne", "nh", "nj", "nm", "nv", "ny", "oh", "ok", "or", "pa", "ri", "sc", 
    #           "sd", "tn", "tx", "ut", "va", "vt", "wa", "wi", "wv", "wy"]
    
    states = ["ga"]

    # alphabets = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]

    alphabets = ["a"]

    for state in states:
        print(state, "********state********")
        for alphabet in alphabets:
            driver.get(f"https://www.yellowpages.com/state-{state}?page={alphabet}")
            time.sleep(3)

            provider_types = {
                # 'diagnostic-center': 'medical diagnostic center',
                # 'primary-care': 'primary care',
                # 'urgent-care': 'urgent care',   
                # 'vision-care': 'medical vision care',
                # 'imaging-labs': 'medical imaging labs',
                'chiropractics': 'chiropractics',
                'dental-care': 'dental care',
                # 'physiotherapy': 'physiotherapy'
            }



            cities_content = driver.find_element(By.CLASS_NAME, 'list-content')
            cities_url_elements = cities_content.find_elements(By.TAG_NAME, 'a')
            # cities_url = [a.get_attribute('href') for a in cities_url_elements]
            # cities = [a.text for a in cities_url_elements]

            # cities_url = ["https://www.yellowpages.com/acme-wa", "https://www.yellowpages.com/alger-wa", "https://www.yellowpages.com/algona-wa"]
            # cities = ["airway-heights", "albion", "alger", "algona"]

            cities_url = ["https://www.yellowpages.com/alpharetta-ga"]
            cities = ["alpharetta"]

            for city_url,city_name in zip(cities_url, cities):
                print(city_url)
                for key, value in provider_types.items():
                    print(f"****Processing provider type: {key}****")

                    all_urls = []
                    
                    try:
                        driver.get(f'{city_url}/doctors')
                        time.sleep(2)
                        
                        search_bar = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.ID, 'query'))
                        )
                        search_bar.clear()
                        search_bar.send_keys(f"{value}")
                        time.sleep(3)
                        
                        form = driver.find_element(By.ID, 'search-form')
                        form.find_element(By.TAG_NAME, 'button').click()
                        time.sleep(3)
                        
                    except Exception as e:
                        print(f"Error setting up search: {e}")
                        continue

                    page = 1
                    consecutive_failures = 0
                    max_failures = 3
            
                    try:
                        while page < 100:
                            print(f"Collecting URLs from Page: {page}")
                            
                            try:
                                WebDriverWait(driver, 15).until(
                                    EC.presence_of_element_located((By.CLASS_NAME, 'result'))
                                )
                            except TimeoutException:
                                print("No results found on this page")
                                break
                            
                            page_urls_before = len(all_urls)
                            cards = driver.find_elements(By.CLASS_NAME, 'result')
                            
                            for card in cards:
                                try:
                                    anchor_tag = card.find_element(By.CLASS_NAME, 'business-name')
                                    url = anchor_tag.get_attribute('href')
                                    if url and url not in all_urls:
                                        all_urls.append(url)
                                except Exception as e:
                                    print(f"Error extracting URL from card: {str(e)}")
                            
                            page_urls_collected = len(all_urls) - page_urls_before
                            print(f"Collected {page_urls_collected} URLs from page {page}. Total: {len(all_urls)}")
                            
                            if page_urls_collected == 0:
                                consecutive_failures += 1
                                if consecutive_failures >= max_failures:
                                    print("No new URLs found for multiple pages, stopping")
                                    break
                            else:
                                consecutive_failures = 0
                            
                            try:
                                time.sleep(random.uniform(2, 4))
                                remove_interfering_elements(driver)
                                pagination = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.CLASS_NAME, 'pagination'))
                                )
                                next_button = pagination.find_element(By.CLASS_NAME, 'next')
                                
                                if "disabled" in next_button.get_attribute("class"):
                                    print("Reached last page - next button disabled")
                                    break
                                
                                print("Attempting to navigate to next page...")
                                click_success = robust_click(driver, next_button)
                                
                                if not click_success:
                                    print("All click strategies failed, trying URL navigation")
                                    if not navigate_by_url(driver, city_url, page + 1):
                                        print("URL navigation also failed")
                                        break
                                
                                page += 1
                                time.sleep(random.uniform(3, 5))
                                
                                try:
                                    WebDriverWait(driver, 10).until(
                                        EC.staleness_of(cards[0])
                                    )
                                except:
                                    pass
                                
                            except TimeoutException:
                                print("Timeout waiting for pagination elements")
                                break
                            except Exception as e:
                                print(f"Error navigating to next page: {str(e)}")
                                if page < 99 and navigate_by_url(driver, city_url, page + 1):
                                    page += 1
                                    time.sleep(3)
                                    continue
                                break
                                
                    except Exception as e:
                        print(f"Error during URL collection: {str(e)}")
                    
                    print(f"Total URLs collected for {value}: {len(all_urls)}")
                    all_urls = list(set(all_urls))
                    print(f"Unique URLs after deduplication: {len(all_urls)}")
                    
                    if all_urls:
                        urls_to_csv(all_urls, state, city_name, key)
                        # driver, last_init_time = scrape_url(all_urls, driver, key, last_init_time, state, city_name)
    
    try:
        driver.quit()
    except:
        pass


if __name__ == "__main__":
    scrape_yellow_pages()