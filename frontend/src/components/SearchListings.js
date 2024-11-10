// src/components/SearchListings.js
import React, { useState } from 'react';
import axios from 'axios';
import './SearchListings.css';

const SearchListings = () => {
    const [postcode, setPostcode] = useState('');
    const [priceMin, setPriceMin] = useState('');
    const [priceMax, setPriceMax] = useState('');
    const [type, setType] = useState('');
    const [listings, setListings] = useState([]);

    const handleSearch = async () => {
        const response = await axios.get('http://localhost:8000/api/listings', {
            params: {
                postcode,
                price_min: priceMin,
                price_max: priceMax,
                type
            }
        });
        setListings(response.data);
    };

    return (
        <div className="search-container">
            <h1>Search Listings</h1>
            <div>
                <input
                    type="text"
                    placeholder="Postcode"
                    value={postcode}
                    onChange={(e) => setPostcode(e.target.value)}
                />
                <input
                    type="number"
                    placeholder="Min Price"
                    value={priceMin}
                    onChange={(e) => setPriceMin(e.target.value)}
                />
                <input
                    type="number"
                    placeholder="Max Price"
                    value={priceMax}
                    onChange={(e) => setPriceMax(e.target.value)}
                />
                <select
                    value={type}
                    onChange={(e) => setType(e.target.value)}
                >
                    <option value="">Select Type</option>
                    <option value="apartment">Apartment</option>
                    <option value="house">House</option>
                    <option value="townhouse">Townhouse</option>
                </select>
                <button onClick={handleSearch}>Search</button>
            </div>
            <div className="lsiting-container">
                {listings.map((listing) => (
                    <div key={listing.id}>
                        <h2>{listing.title}</h2>
                        <p>{listing.description}</p>
                        <p>Postcode: {listing.postcode}</p>
                        <p>Price: ${listing.price}</p>
                        <p>Type: {listing.type}</p>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default SearchListings;