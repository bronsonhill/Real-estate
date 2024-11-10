@extends('layouts.app')

@section('content')
    <h1>Listings</h1>
    @foreach ($listings as $listing)
        <div>
            <h2>{{ $listing->title }}</h2>
            <p>{{ $listing->description }}</p>
            <p>Location: {{ $listing->location }}</p>
            <p>Price: ${{ $listing->price }}</p>
            <p>Type: {{ $listing->type }}</p>
        </div>
    @endforeach
@endsection