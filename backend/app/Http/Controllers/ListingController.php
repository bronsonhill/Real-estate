<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Listing;

class ListingController extends Controller
{
    public function filteredSearch(Request $request)
    {
        $postcode = $request->input('postcode');
        $minPrice = $request->input('min_price');
        $maxPrice = $request->input('max_price');
        $type = $request->input('type');
        $squaredMetres = $request->input('square_metres');
        $listing_id = $request->input('listing_id');

        $query = Listing::query();

        if ($postcode) {
            $query->where('postcode', $postcode);
        }

        if ($minPrice && $maxPrice) {
            $query->whereBetween('price', [$minPrice, $maxPrice]);
        }

        if ($type) {
            $query->where('property_type', $type);
        }

        if ($squaredMetres) {
            $query->whereNot('square_metres', $squaredMetres);
        }

        if ($listing_id) {
            $query->where('listing_id', $listing_id);
        }

        $listings = $query->get();

        return response()->json($listings);
    }
}
