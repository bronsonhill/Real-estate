import sqlite3
import csv

# Load suburb data from the CSV file
with open('tools/postcodes.csv', 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    next(csv_reader)  # Skip the header row
    suburb_list = [row for row in csv_reader]

# Set up SQLite database
conn = sqlite3.connect('../database.db')
c = conn.cursor()

# Create a table for suburbs if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS suburbs (
                postcode TEXT,
                suburb_name TEXT,
                state_name TEXT,
                state_code TEXT,
                latitude REAL,
                longitude REAL,
                accuracy INTEGER
            )''')

# Load suburbs data into the database
for row in suburb_list:
    postcode, place_name, state_name, state_code, latitude, longitude, accuracy = row
    print("postcode:",postcode)
    print("accuracy:",accuracy)
    c.execute('''INSERT INTO suburbs (postcode, suburb_name, state_name, state_code, latitude, longitude, accuracy) 
                 VALUES (?, ?, ?, ?, ?, ?, ?)''', 
              (postcode, place_name, state_name, state_code, float(latitude), float(longitude), int(accuracy)))

# Commit the changes after loading the suburbs data
conn.commit()
conn.close()

print("Suburbs have been loaded into the database.")