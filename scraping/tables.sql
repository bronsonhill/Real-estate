

CREATE TABLE listings (
    listing_id INTEGER PRIMARY KEY AUTOINCREMENT,
    suburb TEXT NOT NULL,
    postcode TEXT NOT NULL,
    address TEXT NOT NULL,
    property_type TEXT NOT NULL,
    price TEXT,
    link TEXT,
    listing_tag TEXT,
    listing_type TEXT,
    bathrooms TEXT,
    parking_spaces TEXT,
    square_metres TEXT,
    oldest_scraped_at DATETIME NOT NULL,
    latest_scraped_at DATETIME NOT NULL,
    bedrooms INTEGER NOT NULL,
);


CREATE TABLE progress (
    progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
    suburb_name TEXT NOT NULL,
    postcode TEXT NOT NULL,
    property_type TEXT NOT NULL,
    category TEXT NOT NULL,
    bedrooms INTEGER NOT NULL,
    page_num INTEGER NOT NULL,
    scraped_at DATETIME NOT NULL,
    status TEXT NOT NULL,
    UNIQUE (suburb_name, postcode, property_type, category, bedrooms)
);

