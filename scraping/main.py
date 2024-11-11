from itertools import product
from scraper import scrape_page
from DatabaseHandler import DatabaseHandler
import json
from multiprocessing import Pool
import os
import sqlite3
import subprocess

POOLS = 1

with open('scraping/config.json', 'r') as config_file:
    config = json.load(config_file)

def initialize_suburb_list(config):
    # Check if the table exists in the SQLite database
    db_handler = DatabaseHandler(config['db_path'])
    table_exists = db_handler.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='suburbs';").fetchone()

    # If the table does not exist, run the suburb_db_script.py file
    if not table_exists:
        from tools.suburbs_to_db import load_suburbs_to_db
        load_suburbs_to_db(config['suburbs_path'], config['db_path'])

    # Load suburb list from the SQLite database
    suburb_list = db_handler.cursor.execute("SELECT suburb_name, postcode FROM suburbs WHERE state_code = ?", (config['suburb_state_code'],)).fetchall()
    db_handler.close()
    
    return suburb_list


def prepare_params_list(suburb_list):
    # Property types to iterate through
    property_types = ['apartment', 'house', 'town-house']

    # Listing categories to iterate through
    listing_types = ['sale', 'rent', 'sold-listings']

    # Prepare parameters list for multiprocessing
    params_list = []
    for suburb_name, postcode in suburb_list:
        suburb_name_formatted = suburb_name.lower().replace(' ', '-')
        suburb = f"{suburb_name_formatted}-vic-{postcode}"
        for property_type, category, bedrooms in product(property_types, listing_types, range(1, 6)):
            params_list.append((suburb, postcode, property_type, category, bedrooms))
    
    return params_list


suburb_list = initialize_suburb_list(config)
params_list = prepare_params_list(suburb_list)


# Run scraping with multiprocessing
if __name__ == "__main__":
    if POOLS > 1:
        with Pool(processes=POOLS) as pool:
            pool.map(scrape_page, params_list)
    else:
        for params in params_list:
            scrape_page(params)
