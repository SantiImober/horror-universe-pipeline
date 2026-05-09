import requests
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TMDB_TOKEN")
BASE_URL = "https://api.themoviedb.org/3"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "accept": "application/json"
}

RAW_PATH = "data/raw"

def get_horror_movies(page=1):
    """Trae películas de terror desde TMDB."""
    url = f"{BASE_URL}/discover/movie"
    params = {
        "with_genres": 27,
        "sort_by": "popularity.desc",
        "page": page
    }
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()

def extract_all_movies(max_pages=10):
    """Extrae múltiples páginas y guarda raw en disco."""
    all_movies = []
    
    for page in range(1, max_pages + 1):
        print(f"Extrayendo página {page}/{max_pages}...")
        data = get_horror_movies(page=page)
        all_movies.extend(data["results"])
    
    # Guardar raw con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{RAW_PATH}/tmdb_horror_movies_{timestamp}.json"
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_movies, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ {len(all_movies)} películas guardadas en {filename}")
    return filename

if __name__ == "__main__":
    extract_all_movies(max_pages=10)