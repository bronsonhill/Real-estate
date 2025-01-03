import sqlite3
from time import sleep
import logging

logger = logging.getLogger(__name__)

class DatabaseHandler:
    def __init__(self, db_path):
        try:
            self.conn = sqlite3.connect(db_path, check_same_thread=False)
            self.cursor = self.conn.cursor()
            self.conn.execute('PRAGMA journal_mode=WAL;')  # Use Write-Ahead Logging for better concurrency
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to the database: {e}")
            raise

    def update_progress(self, suburb, postcode, property_type, listing_type, bedrooms, page_num, status, scraped_at):
        query = '''UPDATE progress SET page_num = ?, scraped_at = ?, status = ? 
                   WHERE suburb_name = ? AND postcode = ? AND property_type = ? 
                   AND listing_type = ? AND bedrooms = ?'''
        params = (page_num, scraped_at, status, suburb, postcode, property_type, listing_type, bedrooms)
        self.execute_with_retry(query, params)
        if self.cursor.rowcount == 0:
            query = '''INSERT INTO progress (suburb_name, postcode, property_type, listing_type, bedrooms, page_num, scraped_at, status) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
            params = (suburb, postcode, property_type, listing_type, bedrooms, page_num, scraped_at, status)
            self.execute_with_retry(query, params)

    def get_progress(self, suburb, postcode, property_type, listing_type, bedrooms):
        query = '''SELECT page_num, scraped_at, status FROM progress 
                   WHERE suburb_name = ? AND postcode = ? AND property_type = ? 
                   AND listing_type = ? AND bedrooms = ?'''
        params = (suburb, postcode, property_type, listing_type, bedrooms)
        self.execute_with_retry(query, params)
        return self.cursor.fetchone()

    def update_listing(self, suburb, postcode, address, property_type, price, link, listing_tag, listing_type, bathrooms, parking_spaces, square_metres, current_time, bedrooms):
        # Check if listing exists
        self.execute_with_retry('''SELECT listing_id, oldest_scraped_at FROM listings WHERE address = ? AND suburb = ? AND postcode = ? AND property_type = ? AND listing_type = ? AND price = ? AND link = ? AND listing_tag = ? AND bathrooms = ? AND parking_spaces = ? AND square_metres = ? AND bedrooms = ?''',
                                (address, suburb, postcode, property_type, listing_type, price, link, listing_tag, bathrooms, parking_spaces, square_metres, bedrooms))
        result = self.cursor.fetchone()
        if result:
            listing_id, oldest_scraped_at = result
            # Update latest scraped date
            query = '''UPDATE listings SET latest_scraped_at = ? WHERE listing_id = ?'''
            params = (current_time, listing_id)
            self.execute_with_retry(query, params)
        else:
            # Insert new listing
            query = '''INSERT INTO listings (suburb, postcode, address, property_type, price, link, listing_tag, listing_type, bathrooms, parking_spaces, square_metres, oldest_scraped_at, latest_scraped_at, bedrooms) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
            params = (suburb, postcode, address, property_type, price, link, listing_tag, listing_type, bathrooms, parking_spaces, square_metres, current_time, current_time, bedrooms)
            self.execute_with_retry(query, params)

    def execute_with_retry(self, query, params, max_retries=5, wait_time=0.5):
        retries = 0
        while retries < max_retries:
            try:
                self.cursor.execute(query, params)
                self.conn.commit()
                break
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e):
                    retries += 1
                    sleep(wait_time)  # Wait before retrying
                else:
                    raise
        if retries == max_retries:
            raise sqlite3.OperationalError("Database is locked after multiple retries.")

    def close(self):
        self.conn.close()