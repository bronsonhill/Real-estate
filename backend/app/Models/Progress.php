<?php
// Progress.php
use Illuminate\Database\Eloquent\Model;

class Progress extends Model {
    protected $table = 'progress';
    protected $primaryKey = 'progress_id';
    public $timestamps = false;
    protected $fillable = [
        'suburb_name', 'postcode', 'property_type', 'category', 'bedrooms', 'page_num', 'scraped_at', 'status'
    ];
}