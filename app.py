from flask import Flask, jsonify, request
from dotenv import load_dotenv
import os
import requests
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Initialize Flask application
app = Flask(__name__)

# Function to authenticate API key


def authenticate_api_key(api_key):
    expected_api_key = os.getenv("API_KEY")
    print(f"Received API Key: {api_key}")
    print(f"Expected API Key: {expected_api_key}")
    return api_key == expected_api_key

# Function to fetch movie details from TMDB API


def fetch_movie_details(movie_name):
    api_key = os.getenv("TMDB_API_KEY")
    base_url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": api_key,
        "query": movie_name
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    return data.get("results", [])

# Function to fetch movie cast from TMDB API


def fetch_movie_cast(movie_id):
    api_key = os.getenv("TMDB_API_KEY")
    base_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits"
    params = {
        "api_key": api_key
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    return data.get("cast", [])

# Endpoint to get all movies


@app.route('/movies', methods=['GET'])
def get_all_movies():
    # Get API key from request header
    api_key = request.headers.get('X-API-Key')
    # Authenticate the API key
    if not api_key or not authenticate_api_key(api_key):
        return jsonify({"error": "Unauthorized"}), 401

    # Fetch movie details from TMDB API
    movie_list = fetch_movie_details("")
    return jsonify(movie_list)

# Endpoint to get movie details by name


@app.route('/movies/<string:movie_name>', methods=['GET'])
def get_movie_by_name(movie_name):
    # Get API key from request header
    api_key = request.headers.get('X-API-Key')
    # Authenticate the API key
    if not api_key or not authenticate_api_key(api_key):
        return jsonify({"error": "Unauthorized"}), 401

    # Fetch movie details from TMDB API
    movie_details = fetch_movie_details(movie_name)
    if movie_details:
        movie = movie_details[0]
        release_date = movie["release_date"]
        release_year = datetime.strptime(release_date, "%Y-%m-%d").year

        # Fetch movie cast from TMDB API
        cast = fetch_movie_cast(movie["id"])

        # Create relevant details JSON
        relevant_details = {
            "title": movie["title"],
            "release_year": release_year,
            "plot": movie["overview"],
            "cast": cast,
            "rating": movie["vote_average"]
        }
        return jsonify(relevant_details)
    return jsonify({"error": "Movie not found"}), 404


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
