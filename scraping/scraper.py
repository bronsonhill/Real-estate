import time
import random
import timeit
import json
import logging
from itertools import product
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException, StaleElementReferenceException, ElementNotInteractableException
from datetime import datetime, timedelta

from DatabaseHandler import DatabaseHandler


# Load configuration from file
with open('scraping/config.json', 'r') as config_file:
    config = json.load(config_file)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
MAX_RETRIES = 1
PAGE_TIMEOUT = (20, 40)
SUCCESS_STATUS = "success"
FAILURE_STATUS = "failure"
NO_LISTINGS_STATUS = "no_listings"
RECENT_SCRAPE_WINDOW_HOURS = 24  # Time window in hours to skip recently scraped pages

# Set up Selenium with Chrome WebDriver
def setup_driver(driver_path, options):
    service = Service(driver_path)
    options.page_load_strategy = 'eager'  # Set page load strategy to 'eager'
    return webdriver.Chrome(service=service, options=options)

chrome_options = Options()
# Disable images and unnecessary resources to speed up loading
prefs = {
    "profile.managed_default_content_settings.images": 2,  # Disable images
    "profile.default_content_setting_values.notifications": 2,  # Disable notifications
    "profile.managed_default_content_settings.css": 2  # Optionally disable CSS if not needed
}
chrome_options.add_experimental_option("prefs", prefs)

# Use existing settings in your code
for option in config['chrome_options']:
    chrome_options.add_argument(option)

def get_driver():
    return setup_driver(config['driver_path'], chrome_options)

def extract_listing_data(listing):
    data = {}
    try:
        data['address'] = listing.find_element(By.XPATH, ".//a[contains(@class, 'address')]").text.strip()
    except NoSuchElementException:
        data['address'] = 'N/A'

    try:
        data['price'] = listing.find_element(By.XPATH, ".//div[@data-testid='listing-card-price-wrapper']").text.strip()
    except NoSuchElementException:
        data['price'] = 'N/A'

    try:
        data['link'] = listing.find_element(By.XPATH, ".//a[contains(@class, 'address')]").get_attribute('href').strip()
    except NoSuchElementException:
        data['link'] = 'N/A'

    try:
        data['listing_tag'] = listing.find_element(By.XPATH, ".//div[@data-testid='listing-card-tag']//span").text.strip()
    except NoSuchElementException:
        data['listing_tag'] = 'N/A'

    try:
        data['bathrooms'] = listing.find_element(By.XPATH, ".//span[@data-testid='property-features-text-container' and contains(., 'Bath')]").text.strip()
    except NoSuchElementException:
        data['bathrooms'] = 'N/A'

    try:
        data['parking_spaces'] = listing.find_element(By.XPATH, ".//span[@data-testid='property-features-text-container' and contains(., 'Parking')]").text.strip()
    except NoSuchElementException:
        data['parking_spaces'] = 'N/A'

    try:
        data['square_metres'] = listing.find_element(By.XPATH, ".//span[@data-testid='property-features-text-container' and contains(., 'm²')]").text.strip()
    except NoSuchElementException:
        data['square_metres'] = 'N/A'

    return data

def scrape_page(params):
    suburb, postcode, property_type, category, bedrooms = params
    db_handler = DatabaseHandler(config['db_path'])

    # Check if recently scraped
    recent_scrape_cutoff = datetime.now() - timedelta(hours=RECENT_SCRAPE_WINDOW_HOURS)
    last_scraped = db_handler.get_progress(suburb, postcode, property_type, category, bedrooms)
    if last_scraped and datetime.strptime(last_scraped[1], '%Y-%m-%d %H:%M:%S') > recent_scrape_cutoff:
        logger.info(f"Skipping recently scraped data for {suburb}, {property_type}, {category}, {bedrooms} bedrooms.")
        db_handler.close()
        return

    driver = get_driver()
    max_retries = MAX_RETRIES
    page_num = 1

    while True:
        retry_count = 0
        while retry_count < max_retries:
            try:
                # Construct URL and load page
                url = f"https://www.domain.com.au/{category}/{suburb}/{property_type}/{bedrooms}-bedroom{'s' if bedrooms > 1 else ''}/?ssubs=0&page={page_num}"
                logger.info(f"Scraping URL: {url}")
                start_time = timeit.default_timer()
                driver.get(url)
                elapsed = timeit.default_timer() - start_time
                logger.info(f"Page load took {elapsed:.2f} seconds.")

                # Wait for essential elements only if present
                dynamic_timeout = random.uniform(*PAGE_TIMEOUT)
                try:
                    WebDriverWait(driver, dynamic_timeout).until(
                        EC.presence_of_element_located((By.XPATH, "//ul[@data-testid='results']"))
                    )
                except TimeoutException:
                    logger.info(f"No listings found after timeout on page {page_num} for {bedrooms} bedrooms in {suburb}. Ending page scraping.")
                    db_handler.update_progress(suburb, postcode, property_type, category, bedrooms, page_num, NO_LISTINGS_STATUS, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    driver.quit()
                    db_handler.close()
                    return

                # Extract listings
                listings_xpath = "//ul[@data-testid='results']//li[contains(@data-testid, 'listing-') or @data-testid='listing-card-wrapper-elite']"
                listings = driver.find_elements(By.XPATH, listings_xpath)
                if not listings:
                    if page_num == 1:
                        status = NO_LISTINGS_STATUS
                    else:
                        status = SUCCESS_STATUS
                    logger.info(f"No listings found on page {page_num} for {bedrooms} bedrooms in {suburb}. Ending page scraping.")
                    db_handler.update_progress(suburb, postcode, property_type, category, bedrooms, page_num, status, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    driver.quit()
                    db_handler.close()
                    return

                scrape_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # Extract and save each listing's data
                for listing in listings:
                    try:
                        data = extract_listing_data(listing)
                        db_handler.update_listing(suburb, postcode, data['address'], property_type, data['price'], data['link'], data['listing_tag'], category, data['bathrooms'], data['parking_spaces'], data['square_metres'], scrape_time, bedrooms)
                    except StaleElementReferenceException as e:
                        logger.warning(f"StaleElementReferenceException while extracting data from listing: {e}")
                        continue  # Skip this listing
                    except ElementNotInteractableException as e:
                        logger.warning(f"ElementNotInteractableException while interacting with listing: {e}")
                        continue  # Skip this listing

                logger.info(f"Page {page_num} for {bedrooms} bedrooms in {suburb} scraped successfully.")
                
                page_num += 1
                break

            except NoSuchElementException as e:
                logger.error(f"NoSuchElementException occurred: {e}")
                retry_count += 1
            except TimeoutException as e:
                logger.error(f"TimeoutException occurred: {e}")
                retry_count += 1
            except StaleElementReferenceException as e:
                logger.error(f"StaleElementReferenceException occurred: {e}")
                retry_count += 1
            except WebDriverException as e:
                retry_count += 1
                logger.error(f"WebDriverException occurred: {e}. Retrying ({retry_count}/{max_retries})...")
                time.sleep(5)

            if retry_count > max_retries:
                logger.info(f"Failed to scrape page {page_num} for {bedrooms} bedrooms in {suburb}.")
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                db_handler.update_progress(suburb, postcode, property_type, category, bedrooms, page_num, FAILURE_STATUS, current_time)
                driver.quit()
                db_handler.close()
                return