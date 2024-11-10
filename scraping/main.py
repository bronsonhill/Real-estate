from itertools import product
from scraper import scrape_page
from DatabaseHandler import DatabaseHandler
import json
from multiprocessing import Pool


with open('scraping/config.json', 'r') as config_file:
    config = json.load(config_file)

# Load suburb list from the SQLite database
db_handler = DatabaseHandler(config['db_path'])
suburb_list = db_handler.cursor.execute("SELECT suburb_name, postcode FROM suburbs WHERE state_code = ?", (config['suburb_state_code'],)).fetchall()
db_handler.close()

# Property types to iterate through
types = ['apartment', 'house', 'town-house']

# Listing categories to iterate through
categories = ['sale', 'rent', 'sold-listings']

# Prepare parameters list for multiprocessing
params_list = []
for suburb_name, postcode in suburb_list:
    suburb_name_formatted = suburb_name.lower().replace(' ', '-')
    suburb = f"{suburb_name_formatted}-vic-{postcode}"
    for property_type, category, bedrooms in product(types, categories, range(1, 6)):
        params_list.append((suburb, postcode, property_type, category, bedrooms))

# Run scraping with multiprocessing
if __name__ == "__main__":
    with Pool(processes=1) as pool:  # Adjust the number of processes based on your system
        pool.map(scrape_page, params_list)
