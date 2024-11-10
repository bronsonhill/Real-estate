<?php
// Listing.php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Factories\HasFactory;

class Listing extends Model {
    use HasFactory;
    
    protected $table = 'listings';
    protected $primaryKey = 'listing_id';
    public $timestamps = false;
    protected $fillable = [
        'suburb', 'postcode', 'address', 'property_type', 'price', 'link', 'listing_tag', 'category', 'bathrooms', 'parking_spaces', 'square_metres', 'oldest_scraped_at', 'latest_scraped_at', 'bedrooms'
    ];
}