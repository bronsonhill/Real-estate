import React from 'react';
import SearchListings from './components/SearchListings';
import './App.css';
import Header from './components/Header';

const App = () => {
    return (
        <div className="App">
          <Header />
            <SearchListings />
        </div>
    );
};

export default App;
