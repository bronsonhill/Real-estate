<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\ListingController;

Route::get('/', function () {
    return view('welcome');
});

Route::get('/listings', [ListingController::class, 'filteredSearch']);
