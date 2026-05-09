import requests
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TMDB_TOKEN")

BASE_URL = "https://api.themoviedb.org/3"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "accept": "application/json"
}

def get_horror_movies(page=1):
    """Trae películas de terror desde TMDB."""
    url = f"{BASE_URL}/discover/movie"
    params = {
        "with_genres": 27,  # 27 = Horror en TMDB
        "sort_by": "popularity.desc",
        "page": page
    }
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    data = get_horror_movies(page=1)
    print(f"Total películas encontradas: {data['total_results']}")
    print(f"Películas en página 1: {len(data['results'])}")
    print(f"Primera película: {data['results'][0]['title']}")